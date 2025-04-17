from hardware import Leg, Servo
import machine
import time

leg_fl = Leg(Servo(0), 4, Servo(1), 8, Leg.Side.Left)
leg_bl = Leg(Servo(2), 4, Servo(3), 8, Leg.Side.Left)
leg_fr = Leg(Servo(4), 4, Servo(5), 8, Leg.Side.Right)
leg_br = Leg(Servo(6), 4, Servo(7), 8, Leg.Side.Right)

legs = (leg_br, leg_fr, leg_fl, leg_bl)

target = (11,0)
leg_br.move_to_fast(target)
leg_bl.move_to_fast(target)
leg_fr.move_to_fast(target)
leg_fl.move_to_fast(target)

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

with open("index.html") as indx_file:
    INDEX = indx_file.read()
    print(INDEX)

# Webserver stuff
import network
import microdot

app = microdot.Microdot()

def setup_network():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid="jrit-dog-robot", security=4, key="bark&bark")
    ap.active(True)
    while not ap.active:
        time.sleep_ms(100)
    tmp = ap.ifconfig()
    print("Dog IP address:", tmp[0])

@app.route("/")
def index_page(req):
    return microdot.Response(body=INDEX, headers={"Content-type": "text/html"})

def index_redirect():
    return microdot.Response(
        status_code=303,
        reason="API Endpoint",
        headers={
            "Location": "/",
        }
    )

@app.route("/sit")
def route_sit(req):
    print("sit")
    motion2()
    return index_redirect()

@app.route("/stand")
def route_stand(req):
    print("stand")
    motion1()
    return index_redirect()
        
@app.route("/walk")
def route_walk(req):
    print("stand")
    motion1()
    return index_redirect()

#print(leg_bl.servo2.current_angle)
#leg_bl.servo2.move_to_fast(0)
#leg_fl.servo2.move_to_fast(0)

setup_network()
app.run(port=80)
