"""Hardware abstractions for a robot dog"""

import machine
import math
import time


class Servo(object):
    """A simple servo abstraction that makes it easier to conrol movements.
    Angles are in degrees."""
    def __init__(self, pin: int):
        """Initialize a servo object
        :param pin: The GPIO pin number that controls the pwm of the servo
        """
        # set the reference PWM duties for -90, 0, and 90 degrees
        self.PWM_MIN = 0.6 
        self.PWM_MID = 1.6
        self.PWM_MAX = 2.6

        # get the conversion factor from degrees to pwm duty nanoseconds
        self.DEG_TO_MS = (self.PWM_MAX - self.PWM_MIN) / 180

        self.pwm = machine.PWM(machine.Pin(pin))
        self.pwm.freq(50)  # set pwm frequency that servo desires

        self.current_angle = 0

    def move_to_timed(self, angle, time_seconds):
        """Move to a given angle over a given amount of time
        (steps in 100ms increments)
        :param angle: angle in degrees for servo to go to
        :param time: time in seconds for motion to take
        """
        steps = time_seconds * 10  # move every tenth of a second
        # get the angular size of each step
        step_size = (angle - self.current_angle) / steps
        # step until reaching the desired angle

        for _ in range(steps):
            self.move_to_fast(self.current_angle + step_size)
            time.sleep_ms(100)  # sleep for a tenth of a second

        # ensure that we go to the correct angle
        self.move_to_fast(angle)

    def move_to_fast(self, angle):
        """Move to a given angle as quickly as possible
        :param angle: the angle in degrees for the servo to move to
        """
        # update the current angle
        self.current_angle = angle

        # apply the conversion factor to get the desired duty in milliseconds
        pwm_ms = self.PWM_MID + self.current_angle*self.DEG_TO_MS
        pwm_ns = int(pwm_ms * 1_000_000)

        # set duty (in nanoseconds)
        self.pwm.duty_ns(pwm_ns)

class Leg(object):
    """A simple 2DoF leg"""
    class Side():
        Left = 1
        Right = 0
    
    def __init__(self, servo1: Servo, len1: float, servo2: Servo, len2: float,
                 side: Side):
        """Create a Leg.
        :param servo1: The first (body-most) servo in the leg
        :param len1: The length of the first leg segment (dist between joints)
        :param servo2: The second (knee) servo in the leg
        :param len2: The length of the second leg segment (dist to foot)
        :param side: The side the leg is on (See Leg.Side)
        """
        self.servo1 = servo1
        self.len1 = len1 

        self.servo2 = servo2
        self.len2 = len2
        
        self.side = side

    # https://osrobotics.org/osr/kinematics/inverse_kinematics.html
    def _inv_kinematics(self, des_x: float, des_y: float) -> list[tuple[float, float]]:
        """Calculates the inverse kinematics for a 2-DoF manipulator
        :param x_des: The x-coordinate of the target point
        :param y_des: The y-coordinate of the target point
        :return: A list of possible joint angle (rads) pairs that would reach
        the destination (most target points within reach will have two
        solutions, one for 'elbow up' and the other for 'elbow down'). ex:
        ((angle1, angle2), (angle1, angle2))
        """
        # the result list
        res = []

        # this is ultimately derived from the law of cosines
        # it tells us the cosine of the second joint's angle
        # (some of this could be cached, if so desired)
        a2_cos = ((des_x**2 + des_y**2 - self.len1**2 - self.len2**2) / 
            (2*self.len1*self.len2))

        # cosine has range [-1,1], so outside that is unreachable
        if abs(a2_cos) > 1:
            # return empty result list
            # it might be handy for our implementation to just return an angle
            # pair that 'stretches' toward the destination (theta, 0)
            return res

        # the angle of the second joint (+ or -, both corresponding to a
        # possible position)
        a2 = math.acos(a2_cos)

        # calculate all possibilities for the first joint's angle
        for a in (a2, -a2):
            k1 = self.len1 + self.len2*math.cos(a)
            k2 = self.len2*math.sin(a)

            a1 = math.atan2(des_y, des_x) - math.atan2(k2, k1)

            res.append((a1, a))

            # |0| = 0, so we just need to calculate once
            if a2 == 0:
                break

        return res

    def move_to_fast(self, target: tuple[float, float]) -> bool:
        """Move to a given target (using ik) as quickly as possible. NOTE:
        Apparently we can't reach close positions because the 2nd servo has to
        rotate more and counteract the 1st.
        :param target: the target for the leg to move to
        :return: whether the target was reachable
        """
        options = self._inv_kinematics(*target)

        if len(options) == 0: return False
        
        # pick an option based on which side the leg is on (so they ultimately
        # face the same way)
        option = self.side if len(options) == 2 else 0
        angle1 = math.degrees(options[option][0])
        angle2 = math.degrees(options[option][1])
        
        # might be trying to go in the wrong direction because of flip?
        if self.side == Leg.Side.Left: angle2 = angle2
        
        offset = 90 if self.side == Leg.Side.Right else 0
        
        self.servo1.move_to_fast(angle1)
        self.servo2.move_to_fast(-angle2+offset)

        return True

    def move_to_timed(self, target: tuple[float, float]) -> bool:
        """Move to a given target (using ik) over a given amount of time.
        :param target: the target for the leg to move to
        :param duration: the duration of time over which for the leg to move
        :return: whether the target was reachable
        """
        raise NotImplemented

class DistSensor(object):
    # measured luminosity of the LED
    LED_LUMINOSITY = 45000

    """A sensor that uses an LDR and LED to roughly detect the distance to
    obstacles.
    """
    def __init__(self, ldr_pin, led_pin):
        """Initialize a distance sensor.
        :param ldr_pin: The ADC/GPIO pin number of the pin connected to the LDR
        :param led_pin: The GPIO pin number of the pin connected to the LED
        """

        # get the ldr ADC pin
        self.ldr = machine.ADC(ldr_pin)
        # get the led
        self.led = machine.Pin(led_pin, machine.Pin.OUT)

    def read(self):
        """Read the sensor, returning the distance detected (very roughly, in
        a unit about as long as an inch, for some reason).
        """
        # the length of time to allow the led and ldr to adjust
        SLEEP_TIME = 100

        # get the ldr reading for when the led is on
        self.led.on()
        # sleep for a bit to let led and ldr adjust
        time.sleep_ms(SLEEP_TIME)
        on = self.ldr.read_u16();

        # get the LDR reading for when the LED is off
        self.led.off()
        # sleep for a bit to let LED and LDR adjust
        time.sleep_ms(SLEEP_TIME)
        off = self.ldr.read_u16();

        # calculate how the LED light affects the reading
        diff = on - off

        # I think since $SA = 4\pi{}r^2$ for a sphere, the diff will fall off
        # by that formula and we can use it to find the distance (though,
        # remember that the light has to go twice as far as the distance to the
        # object!)

        # luminosity distance (meters):
        # dist = \sqrt{luminosity/(4*pi*flux)}
        # (note that our distance will be half this because the light travels
        # both ways

        # somehow measure this
        flux = diff

        # I think because the luminosity and flux are both in ADC units, they
        # cancel out and give us meters
        print(f'flux: {flux}')
        lum_dist = math.sqrt(self.LED_LUMINOSITY / abs(4*math.pi*flux))

        dist = lum_dist

        return dist
