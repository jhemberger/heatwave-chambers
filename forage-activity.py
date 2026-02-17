import RPi.GPIO as GPIO
import os
import time

BEAM_PIN = 27

mc1_pin = 27
#mc2_pin
#mc3_pin
#mc4_pin
#mc5_pin

try:
    f = open('/home/bombus/chamber-01/forage-activity.csv', 'a+', 0)
    if os.stat('/home/bombus/chamber-01/forage-activity.csv').st_size == 0:
        f.write('date,time,sensor,status\n')
except:
    pass

gate_1 = 'mc-entrance'

def break_beam_callback(channel):
    if GPIO.input(BEAM_PIN):
        f.write('{},{},{},{}\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M:%S'), gate_1, 'clear'))
        print("beam unbroken")
    else:
        f.write('{},{},{},{}\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M:%S'), gate_1, 'bee detected'))
        print("beam broken")
            

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BEAM_PIN, GPIO.BOTH, callback=break_beam_callback)

message = input("Press enter to quit\n\n")
GPIO.cleanup()