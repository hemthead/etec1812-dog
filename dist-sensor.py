import machine
import math
import time


# measured luminosity of the LED
LED_LUMINOSITY = ...

class DistSensor(object):
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
        """Read the sensor, returning the distance detected (in meters)"""
        # the length of time to allow the led and ldr to adjust
        SLEEP_TIME = 0.1

        # get the ldr reading for when the led is on
        self.led.on()
        # sleep for a bit to let led and ldr adjust
        time.sleep(SLEEP_TIME)
        on = self.ldr.read_u16();

        # get the LDR reading for when the LED is off
        self.led.off()
        # sleep for a bit to let LED and LDR adjust
        time.sleep(SLEEP_TIME)
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
        flux = ...

        # I think because the luminosity and flux are both in ADC units, they
        # cancel out and give us meters
        lum_dist = math.sqrt(LED_LUMINOSITY / (4*math.pi*flux))

        dist = lum_dist / 2

        return dist
