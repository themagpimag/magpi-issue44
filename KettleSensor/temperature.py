#!/usr/bin/env python

import os
import time
import dot3k.lcd as lcd
import dot3k.joystick as joystick
import dot3k.backlight as backlight
from gpiozero import Buzzer
import RPi.GPIO as GPIO

set_temp = 85
bz = Buzzer(21)
GPIO.setup(12,GPIO.OUT)
GPIO.output(12,GPIO.HIGH)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

temp_sensor = '/sys/bus/w1/devices/28-000006d85491/w1_slave'

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()
    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def temp_light(temperature):
    scale = set_temp - 20
    if temperature < 20:
        return [0,0,255]
    else:
        temp_difference = set_temp - temperature
        backlight_colour = int((scale - temp_difference)*(255/scale))
        return [(0 + backlight_colour), 0 , (255 - backlight_colour)]

@joystick.on(joystick.UP)
def handle_up(pin):
    global set_temp
    set_temp += 1

@joystick.on(joystick.DOWN)
def handle_down(pin):
    global set_temp
    set_temp -= 1
    
while True:
    temperature = read_temp()
    lcd_text = "Water temp: " + str(round(temperature, 1)) + "Set temp: " + str(set_temp)
    lcd.clear()
    lcd.write(lcd_text)
    rgb_colours = temp_light(temperature)
    backlight.rgb(rgb_colours[0], rgb_colours[1], rgb_colours[2])
    if temperature >= set_temp:
        bz.on()
    time.sleep(0.5)
