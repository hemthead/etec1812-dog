from hardware import Leg, Servo

s1 = Servo(0)
s2 = Servo(1)
leg = Leg(s1, 0.5, s2, 0.5)

print(leg.move_to_fast((-0.2,0.8)))

#s1.move_to_fast(90)
