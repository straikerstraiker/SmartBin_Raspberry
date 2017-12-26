from config import *
import RPi.GPIO as GPIO
import time
import picamera
import logging
import datetime
import send
import urllib
import os

import Adafruit_PCA9685
import serial

GPIO.setmode(GPIO.BOARD)

GPIO.setup(BEEPER, GPIO.OUT)
GPIO.output(BEEPER, 0)


camera = picamera.PiCamera()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)  # Setting up logging

UART = serial.Serial(
    port='/dev/serial0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

pwm = Adafruit_PCA9685.PCA9685()

pwm.set_pwm_freq(75)

fake = 1

GPIO.setup(INNER, GPIO.OUT)
GPIO.output(INNER, 0)

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)

WAIT_LIMIT = 8

def open_up():
    pwm.set_pwm(UP_SERVO, 0, OPEN_UP)


def close_up():
    pwm.set_pwm(UP_SERVO, 0, CLOSE_UP)


def close_down():
    pwm.set_pwm(DOWN_SERVO, 0, CLOSE_DOWN)


def pet_down():
    pwm.set_pwm(DOWN_SERVO, 0, PET_DOWN)


def al_down():
    pwm.set_pwm(DOWN_SERVO, 0, AL_DOWN)


def close_lock():
    pwm.set_pwm(LOCK1_SERVO, 0, LOCK1_CLOSE)
    pwm.set_pwm(LOCK2_SERVO, 0, LOCK2_CLOSE)


def open_lock():
    pwm.set_pwm(LOCK1_SERVO, 0, LOCK1_OPEN)
    pwm.set_pwm(LOCK2_SERVO, 0, LOCK2_OPEN)


def make_photo():
    GPIO.output(INNER, 1)
    image_time = datetime.datetime.now()  # Making a unique name of a string from datetime
    image_time = str(image_time)[:19].replace(' ', '').replace('-', '').replace(':', '')
    image_path = '/home/pi/Documents/Photos/' + image_time + '.jpeg'
    camera.resolution = (640, 480)
    camera.brightness = 35
    camera.contrast = 50
    camera.capture(image_path, use_video_port=True)
    GPIO.output(INNER, 0)
    return image_path


def contents_type():
    image = make_photo()
    return send.get_class(image)

def waiting():
    global CurGreen, CurBlue,CurRed
    CurGreen = 4000
    CurRed = 0
    CurBlue = 2000

    pwm.set_pwm(RED,0,CurRed)
    pwm.set_pwm(GREEN, 0, CurGreen)

    pwm.set_pwm(BLUE, 0, CurBlue)
    while True:
        for i in range(1000):
            pwm.set_pwm(GREEN, 0, CurGreen)
            pwm.set_pwm(BLUE, 0,  CurBlue)
            CurGreen -= 2
            CurBlue += 2
            if i % 100 == 0 and UART.read() == b'\x02':
               return

        for i in range(1000):
            pwm.set_pwm(GREEN, 0, CurGreen)
            pwm.set_pwm(BLUE, 0, CurBlue)
            CurGreen += 2
            CurBlue -= 2
            if i % 100 == 0 and UART.read() == b'\x02':
                return

def static_color(port):
    global CurGreen, CurBlue, CurRed	
    port -= 8

    colors = [CurRed,CurGreen,CurBlue]
    while colors[port] != 4000 or sum(colors) != 4000:
        for i in range(3):
            if i == port:
                colors[i] = min(4000,colors[i] + 25)
            else:
                colors[i] = max(0,colors[i] - 25)
            pwm.set_pwm(i + 8, 0, colors[i])

    CurRed = colors[0]
    CurGreen = colors[1]
    CurBlue = colors[2]


def dynamic_color(port):
    global CurGreen, CurBlue, CurRed
    port -= 8

    colors = [0,0,0]
    colors[port] = 4000
    for i in range(3):
        pwm.set_pwm(i + 8, 0, colors[i])

    while colors[port] > 0:
        colors[port] = max(0,colors[port] - 25)
        pwm.set_pwm(port + 8, 0, colors[port])

    while colors[port] < 4000:
        colors[port] = min(4000, colors[port] + 25)
        pwm.set_pwm(port + 8, 0, colors[port])

    CurRed = colors[0]
    CurGreen = colors[1]
    CurBlue = colors[2]


def sonic_check(TRIG,ECHO):
    GPIO.output(TRIG, False)
    time.sleep(0.01)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2) - 0.5

    if (distance > 42) or (distance < 37):
        return True
    return False


def something_in():
    k = 0
    for i in range(30):
        if sonic_check(TRIG1,ECHO1):
            k += 1
        time.sleep(0.0001)
        if sonic_check(TRIG2,ECHO2):
            k += 1
    if k < 10:
        return False
    return True


def cheat_check():
    k = 0
    for i in range(20):
        if sonic_check(TRIG3,ECHO3):
            k += 1
    if k >= 5:
        return False
    return True


def user_reg(user_id):
    user_url = 'http://smartbin35.ru.mastertest.ru/api/checkuser?cardCode=' + user_id
    logging.info(user_id)
    response = urllib.request.urlopen(user_url)
    logging.info(response.read())
    user_status = response.read()
    if user_status == b'true':
        return True
    return False


def reward(user_id, trash_type):
    reward_url = 'http://smartbin35.ru.mastertest.ru/api/bonus?cardCode=' + user_id
    reward_url = reward_url + '&trashType=' + trash_type + '&trashId=2'
    urllib.request.urlopen(reward_url)


def beep():
    GPIO.output(BEEPER, 1)
    time.sleep(0.3)
    GPIO.output(BEEPER, 0)

try:
    time.sleep(1)
    close_lock()
    logging.info("Process started")
    while True:
        # Correct
        close_up()
        close_down()
        close_lock()
        
        waiting()
        user = UART.read(12).decode('utf-8')
        logging.info(user)

        beep()

        if user == "5605B8DF7642":
            open_lock()
            static_color(RED)
            logging.info("The bin is opened for maintenance")
            #reward(user, 'pet')
            while True:
                time.sleep(5)
        reg_stat = True
        try:
            pass
            static_color(GREEN)
            #reg_stat = user_reg(user)
        except:
            static_color(RED)
            time.sleep(1)
        if reg_stat:
            logging.info("User found")
            # Correct
            entry_time = time.time()
            time_exit = False

            while not time_exit:
                find_exit = False
                open_up()
                while (not find_exit) and (not time_exit):
                    time.sleep(0.1)
                    current_time = time.time()
                    if current_time - entry_time > WAIT_LIMIT:
                        time_exit = True
                    if something_in() and cheat_check():
                        find_exit = True

                close_up()
                time.sleep(0.5)
                if not find_exit:
                    continue

                if something_in():
                    time.sleep(0.7)
                    logging.info("Something in")
                    inner_type = ""
                    try:
                        inner_type = contents_type()
                    except:
                        time.sleep(5)
                        time_exit = True

                    entry_time = time.time()
                    find_exit = False
                    if inner_type == 'pet':
                        os.system('mplayer /home/pi/pywork/sounds/ilovetrash.mp3 -af volume=15')
                        pet_down()
                        time.sleep(2.5)
                        close_down()
                        try:
                            pass
                            #reward(user, 'pet')
                        except:
                            time.sleep(0.5)
                        logging.info('Rewarded for pet!')
                        for i in range(2):
                            dynamic_color(GREEN)

                    elif inner_type == 'al':
                        os.system('mplayer /home/pi/pywork/sounds/ilovetrash.mp3 -af volume=15')
                        al_down()
                        time.sleep(2.5)
                        close_down()
                        try:
                            pass
                            #reward(user, 'al')
                        except:
                            time.sleep(0.5)
                        logging.info('Rewarded for al!')
                        for i in range(2):
                            dynamic_color(GREEN)

                    else:
                        open_up()
                        while something_in():
                            for i in range(2):
                                dynamic_color(RED)
                        close_up()
                        time_exit = True
                else:
                    entry_time = time.time()
                    # Correct
            logging.info("Session closed")
            logging.info('****************************')
        else:
            pass
            # Correct

        time.sleep(0.5)
        UART.flushInput()

finally:
    GPIO.cleanup()
    camera.close()