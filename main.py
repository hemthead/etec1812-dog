from hardware import DistSensor
import machine
import time

l = machine.Pin(0, machine.Pin.OUT)

l.on()

r = machine.ADC(0)

sens = DistSensor(0,0)

while True:
    print(sens.read())
    time.sleep_ms(10)