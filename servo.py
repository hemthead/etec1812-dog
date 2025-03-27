import machine
import time


class Servo(object):
    def __init__(self, pin: int):
        """Initialize a servo object
        :param pin: The GPIO pin number that controls the pwm of the servo
        """
        # set the reference PWM duties for -90, 0, and 90 degrees
        self.PWM_MIN = 1
        self.PWM_MID = 2.005

        # get the conversion factor from degrees to pwm duty nanoseconds
        self.DEG_TO_NS = (self.PWM_MID - self.PWM_MIN)*1_000_000 / 90

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
        pwm_ns = self.PWM_MID + self.current_angle*self.DEG_TO_NS

        # set duty (in nanoseconds)
        self.pwm.duty_ns(pwm_ns)
