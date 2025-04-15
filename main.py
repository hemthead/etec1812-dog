from hardware import Leg, Servo
import machine
import time

leg_br = Leg(Servo(20), 4, Servo(19), 8, Leg.Side.Right)
leg_bl = Leg(Servo(16), 4, Servo(15), 8, Leg.Side.Left)
leg_fr = Leg(Servo(22), 4, Servo(21), 8, Leg.Side.Right)
leg_fl = Leg(Servo(18), 4, Servo(17), 8, Leg.Side.Left)

legs = (leg_br, leg_fr, leg_fl, leg_bl)

target = (11,0)
leg_br.move_to_fast(target)
leg_bl.move_to_fast(target)
leg_fr.move_to_fast(target)
leg_fl.move_to_fast(target)

leg_fr.move_to_fast((10,0))

def motion2():
    leg_bl.move_to_fast((9,0))
    leg_br.move_to_fast((9,0))
    time.sleep(2)
    leg_bl.move_to_fast(target)
    leg_br.move_to_fast(target)

def motion1():
    for leg in legs:
        time.sleep(1)
        leg.move_to_fast((9,0))
        time.sleep(1)
        leg.move_to_fast(target)

#motion2()

print(leg_bl.servo2.current_angle)
#leg_bl.servo2.move_to_fast(0)
#leg_fl.servo2.move_to_fast(0)
