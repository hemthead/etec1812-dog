from hardware import Leg, Servo
import machine
import time
import _thread

leg_fl = Leg(Servo(0), 4, Servo(1), 8, Leg.Side.Left)
leg_bl = Leg(Servo(2), 4, Servo(3), 8, Leg.Side.Left)
leg_fr = Leg(Servo(4), 4, Servo(5), 8, Leg.Side.Right)
leg_br = Leg(Servo(6), 4, Servo(7), 8, Leg.Side.Right)

legs = (leg_br, leg_fr, leg_fl, leg_bl)

target = (10.5,-1)
#target = (12,0)
leg_br.move_to_fast(target)
leg_bl.move_to_fast(target)
leg_fr.move_to_fast(target)
leg_fl.move_to_fast(target)

print(leg_fr.servo2.current_angle)
print(leg_fl.servo2.current_angle)


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
        
def legs_goto(target):
    for leg in legs:
        leg.move_to_fast(target)
        
def crouch():
    legs_goto((8.5,target[1]))

def stand():
    legs_goto(target)
        
def jump():
    crouch()
    time.sleep(1)
    legs_goto((12,0))
    time.sleep(1)
    stand()
    
raise_x = 8.5
lower_x = 10.8
extend_y = 3
STEP_POSITIONS = (
    (raise_x,0),
    (raise_x,extend_y),
    (lower_x,extend_y),
    (lower_x,0),
    target,
    )

def step(leg):
    for i in range(len(STEP_POSITIONS)):
        leg.move_to_fast(STEP_POSITIONS[i])
        #time.sleep(0.8)
        time.sleep(0.2)
        
walking = False
def walk():
    while walking:
        for leg in legs:
            step(leg)
            time.sleep(0.5)
    _thread.exit()
            
def dance():
    stand()
    
    for leg in (leg_fl, leg_fr):
        leg.move_to_fast((9,4))

    time.sleep(1)
    stand()

    
    for i in range(3):
        crouch()
        time.sleep(1)
        stand()
        time.sleep(1)
    
    for leg in (leg_fl, leg_fr, leg_bl, leg_br):
        leg.move_to_fast((7,5))
        time.sleep(1)
        leg.move_to_fast(target)
        time.sleep(1)
        
    for i in range(3):
        crouch()
        time.sleep(1)
        stand()
        time.sleep(1)
        
    for leg in (leg_fl, leg_fr):
        leg.move_to_fast((9,4))
    
    time.sleep(1)
    
    stand()
    
    return
    
    for leg in legs:
        step(leg)
        time.sleep(0.5)

#motion2()

with open("index.html") as indx_file:
    INDEX = indx_file.read()

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

@app.route("/lift")
def route_lift(req):
    print("lift")
    motion1()
    return index_redirect()

@app.route("/stand")
def route_stand(req):
    print("stand")
    stand()
    return index_redirect()
        
@app.route("/start-walking")
def route_walk(req):
    global walking
    walking = True
    _thread.start_new_thread(walk, ())

    return index_redirect()

@app.route("/stop-walking")
def route_stop_walk(req):
    global walking
    walking = False

    return index_redirect()

@app.route("/dance")
def route_dance(req):
    print("dance")
    dance()
    return index_redirect()

@app.route("/set-leg", methods=["POST"])
def position_leg(req):
    print(req)
    leg = int(req.form["leg"])
    x = float(req.form["x"])
    y = float(req.form["y"])
    print(leg, x, y)
    legs[leg].move_to_fast((x,y))
    return index_redirect()

setup_network()
app.run(port=80)