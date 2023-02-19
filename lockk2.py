#!/usr/bin/env python3
import sys
# import MySQLdb
from threading import Thread
import threading
import os
from PIL import Image, ImageTk
from db import get_users, add_delivery, add_delivery_msg
import requests
import logging
import time
import datetime
from time import sleep
#
import json
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT)
GPIO.output(13, GPIO.LOW)
# from evdev import InputDevice
from select import select

import tkinter.font as font
from tkinter import PhotoImage
try:
    # python 2
    import Tkinter as tk
    import ttk
except ImportError:
    # python 3
    import tkinter as tk
    from tkinter import ttk

# os.system('python telot.py &$ sleep(10) && kill telot.py')
API_TOKEN = '2124982820:AAG-zVvET6Pcn9sDPiqIYLheaeos5w8T6dI'

ts = str(datetime.datetime.now())


class Fullscreen_Window:


    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title("Three-Factor Authentication Security Door Lock")
        self.frame = tk.Frame(self.tk)
        self.frame.grid()
        self.tk.columnconfigure(0, weight=1)

        # self.tk.wm_attributes('-zoomed', True)
        self.tk.wm_attributes('-fullscreen', True)
        self.state = True
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.config(cursor="none")

        GPIO.output(13, GPIO.LOW)
        self.show_idle()

    def show_idle(self):
        GPIO.output(13, GPIO.LOW)
        self.welcomeLabel = ttk.Label(self.tk, text="Welcome to Everly")
        self.welcomeLabel.config(font='size, 25', justify='center', anchor='s')
        self.welcomeLabel.grid(sticky=tk.N, pady=60)

        logo1 = Image.open('eve.jpg')
        logo = logo1.resize((200, 105), Image.ANTIALIAS)

        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(image=logo)
        logo_label.image = logo
        logo_label.grid(columnspan=3, row=0)
        photo = PhotoImage(file=r"/home/pi/everly/belf.png")
        photo2 = PhotoImage(file=r"/home/pi/everly/staff.png")

        # Resizing image to fit on button
        self.photoimage = photo.subsample(12, 14)
        self.photoimage2 = photo2.subsample(10, 9)
        buttonFont = font.Font(family='Helvetica', size=25, weight='bold')
        buttonFont1 = font.Font(family='Helvetica', size=30, weight='bold')
        self.btn1 = tk.Button(self.tk, text="Staff", font=buttonFont1, bg="#20bebe",
                              fg="white", height=120, width=380, image=self.photoimage2, compound="right",
                              command=self.codeInput)

        self.btn1.grid(sticky=tk.N + tk.S, pady=20)

        self.btn5 = tk.Button(self.tk, text="Delivery/Guest", font=buttonFont, bg="#20bebe", fg="white", height=120,
                              width=380, image=self.photoimage, compound="right", command=self.notify)
        self.btn5.grid(row=3, sticky=tk.S, pady=40)

    def pin_entry_forget(self):
        self.validUser.grid_forget()

        self.enterPINlabel.grid_forget()
        count = 0
        while (count < 12):
            self.btn[count].grid_forget()
            count += 1

    def returnToIdle_fromPINentry(self):
        self.pin_entry_forget()
        GPIO.output(13, GPIO.LOW)
        self.show_idle()

    def returnToIdle_fromPINentered(self):
        self.PINresultLabel.grid_forget()

        self.show_idle()

    def returnToIdle_fromAccessGranted(self):
        #GPIO.output(13,GPIO.LOW)
        self.SMSresultLabel.grid_forget()
        self.show_idle()

    def returnToIdle_fromSMSentered(self):
        self.SMSresultLabel.grid_forget()

        self.show_idle()

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def codeInput(self):
        global pin

        userPin = '333333'

        self.welcomeLabel.grid_forget()
        self.btn1.grid_forget()
        self.btn5.grid_forget()
        self.validUser = ttk.Label(self.tk, text="Welcome to Everly\n %s!", font='size, 15',
                                   justify='center', anchor='center')
        self.validUser.grid(columnspan=3, sticky=tk.W + tk.E)

        self.enterPINlabel = ttk.Label(self.tk, text="Please enter your PIN:", font='size, 18', justify='center',
                                       anchor='center')
        self.enterPINlabel.grid(columnspan=3, sticky=tk.W + tk.E)
        pin = ''

        keypad = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '*', '0', '#',
        ]

        r = 4
        c = 0
        n = 0
        # list(range()) needed for Python3
        self.btn = list(range(len(keypad)))
        for label in keypad:
            # partial takes care of function and argument
            # cmd = partial(click, label)
            # create the button
            self.btn[n] = tk.Button(self.tk, text=label, font='size, 18', width=4, height=1,
                                    command=lambda digitPressed=label: self.verify(digitPressed, userPin))
            # position the button
            self.btn[n].grid(row=r, column=c, ipadx=15, ipady=10)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c > 2:
                c = 0
                r += 1

        self.PINentrytimeout = threading.Timer(10, self.returnToIdle_fromPINentry)
        self.PINentrytimeout.start()

        self.PINenteredtimeout = threading.Timer(5, self.returnToIdle_fromPINentered)

    def verify(self, value, userPin):

        global pin
        global smsCodeEntered
        pin += value
        pinLength = len(pin)

        self.enterPINlabel.config(text="Digits Entered: %d" % pinLength)

        if pinLength == 6:
            self.PINentrytimeout.cancel()
            self.pin_entry_forget()

            if pin == userPin:
                pin_granted = 1
            else:
                pin_granted = 0

            # Log access attempt

            if pin == userPin:
                self.PINresultLabel = ttk.Label(self.tk, text="Welcome")
                self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
                self.PINresultLabel.grid(columnspan=3, sticky=tk.W + tk.E, pady=20)
                GPIO.output(13, GPIO.HIGH)
                self.PINenteredtimeout.start()
            else:
                self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN\nEntered!")

                self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
                self.PINresultLabel.grid(sticky=tk.W + tk.E, pady=210)
                self.PINenteredtimeout.start()

    # def notify(self):
    #
    #     bot_message = 'Delivery at the door\n time:'+ts+ '\nCheck the video stream from this link\n'+'192.168.5.177:8081'
    #     bot_token = '2124982820:AAG-zVvET6Pcn9sDPiqIYLheaeos5w8T6dI'
    #     bot_chatID = ['793913232','1037229974']
    #     for x in bot_chatID:
    #         self.send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + x + '&parse_mode=Markdown&text=' + bot_message
    #         response = requests.get(self.send_text)
    #         response.json()

    def notify(self):
        global API_TOKEN
        users = get_users()
        bot_message = "Delivery at the door!\n time: "+ts+ "\nCheck the video stream from this link\n"
        keyboard = '{"inline_keyboard": [[{"text": "Attend", "callback_data": "delivery:attend"}]]}'
        delivery_id = add_delivery()
        for user in users:
            send_text = 'https://api.telegram.org/bot' + API_TOKEN + '/sendMessage?chat_id=' + user[0] + \
                        '&parse_mode=Markdown&text=' + bot_message + "&reply_markup=" + keyboard
            response = requests.get(send_text)
            msg = response.json()
            if msg['ok']:
                add_delivery_msg(delivery_id, user[0], msg['result']['message_id'])



if __name__ == '__main__':
    w = Fullscreen_Window()
    w.tk.mainloop()