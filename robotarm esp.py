import math, neopixel
from machine import Pin, PWM
from time import sleep
import socket,network
from random import randint
def network_setup(wifiname, password):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    try:
        wifi.connect(wifiname, password)
        sleep(2)
        print(wifi.ifconfig())
        return True
    except:
        print('failed')
        return False
network_setup('ssid','password')
length1 = 13.35
length2 = 13.1
sp = Pin(46)
ep = Pin(11)
bp = Pin(15)
shoulder = PWM(sp, freq=50)
elbow = PWM(ep, freq=50)
base = PWM(bp, freq=50)
led = neopixel.NeoPixel(Pin(48),1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5005))
sock.settimeout(5.0)

def basecalc(z,x):
    baseangle = math.atan(x/(z+0.001))# angle of the base
    newx = math.sqrt(x**2+z**2)#working out the straight line distance from the base to the desired x coordinate
    return baseangle, newx

def calc(x, y):
    change = True
    mag = math.sqrt(x**2 + y**2)#stright line distance to desired point
    if mag > length1+length2:# checking the cooridinates are valid
        print('cooridates out of range')
        return 0,0,False
    elif x< 0:
        print('x cannot be negative')
    elif y<= 0 :
        print('y cannot be negative')
        return 0,0,False
    jointangle = math.acos((length1**2+length2**2-mag**2)/(2*length1*length2))#using the cosine rule to work out the angle at the elbow
    a = math.asin(y/mag)#working out the angle of the vector
    try:
        b = math.asin((math.sin(jointangle)/mag)*length2)#sin rule working out the angle between forearm and vector 
    except:
        b = 0
        change = False
    base = a+b
    return base,jointangle,change

def set(angle, joint):
    min_duty = 500     # ~0.5ms pulse @ 50Hz
    max_duty = 2500     # ~2.5ms pulse @ 50Hz
    duty = int(min_duty + (angle / math.pi) * (max_duty - min_duty))
    joint.duty(int(duty*1023/20000))

def interpolate(oldb,olds,olde,newb,news,newe,smoothfactor):
    coords = []
    deltab = newb-oldb
    deltas = news-olds
    deltae = newe-olde
    for i in range(smoothfactor):
        coords.append([oldb+deltab/smoothfactor*(i+1), olds+deltas/smoothfactor*(i+1),olde+deltae/smoothfactor*(i+1)])
        #adding incraments to the old coordinates until it reaches the new coordinates
    return coords

def start():
    set(0,shoulder)
    set(0,elbow)
    set(math.pi/2, base)


def main():
    try:
        data = str(sock.recvfrom(1024)[0])[2:-1]
    except OSError:
        print('no data received')
        return False
        #return oldb, olda, oldc  # return old values unchanged
    x,y,z = data.split(',')
    
    baseangle, newx= basecalc(float(z),float(x))
    s,e,change = calc(newx,float(y))
    if change:
        sleep(1)
        print(s,e,baseangle)
        set(e,elbow)
        sleep(0.1)
        set(s,shoulder)
        sleep(0.1)   
        set(baseangle,base)
    else:
        print('invalid')

while True:
    main()


    
