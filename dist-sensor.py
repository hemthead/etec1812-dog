import machine
import time


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
        self.led = machine.Pin(led_pin, machine.Pin.OUT)
