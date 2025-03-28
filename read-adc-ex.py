# Name: Wyatt Montgomery
# Name: John Reed
# Name: Rachel Bailey
# Class: ETEC1812.01 
# Assignment: Lab 1

import machine 
import time

V_AT_SHADE_5 = 2
VOLTS_PER_ADC_VAL = 3.3/65535

adc0 = machine.ADC(26) 
led = machine.Pin("LED", machine.Pin.OUT)

while True: 
    value = adc0.read_u16()
    voltage = value * VOLTS_PER_ADC_VAL
    print("ADC0: ",value, "voltage:",voltage, "percentage:",(value/65535)*100) 

    if voltage < (V_AT_SHADE_5):
        led.on()
    else:
        led.off()

    time.sleep(0.25)

