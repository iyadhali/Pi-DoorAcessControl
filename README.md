# Pi-DoorAcessControl
Door access system with Touch based GUI using a Raspberry Pi. Applicable for both servo control doors and magnetic lock based doors

#Before runing the code, make sure the images in the repo are in the same location as defined in the code. Run db.py to create the sql lite database.

#the code lockk2.py is the door lock code made for magnetic door locl systems. external button integration, video calling, random code request and guest alert part is not added to this code yet. To add, take the Door_lock_final.py

#Then run tg.py to run the telegram bot, assuming a bot is created on telegram. ( to create a telegram bot refer to this link https://sendpulse.com/knowledge-base/chatbot/create-telegram-chatbot)

#in the telegram bot chat send /addme to add a new user, /users to check the people bot is substribed to

#Door_lock_final.py is the final code for the loading shutter door, door lock system. The code can open & close the door by changing the polarity of the motor. The a timer thread is used to control the time the relays turn on. The door can also be controlled from an externat button connected to the pi. The door opens and closes when the button is pressed. 

#To run any programs/commands from boot edit the file in the location below and add the program location. Include bash to run shell commands and the commands should be in a .sh file 

sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

#Enter the following command below to start webrtc server(video streaming server). The commands needs to be run before the code. So to run it on when pi is booted create a bash file and the enter the location of the bashfile in sudo nano /etc/xdg/lxsession/LXDE-pi/autostart. Similar to screen auto rotation bash file

uv4l --external-driver --device-name=video0

#you can setup the webrtc streaming by folloeing this guide https://www.highvoltagecode.com/post/webrtc-on-raspberry-pi-live-hd-video-and-audio-streaming

#IMPROVEMENTS
1) rewrite the gui using using pyQt framework for better speed and aethsetics. The tkinter has a lot of limiations including lagging and poor UI
2) intgrate a PIR sensor to stop the door closing when a person is detected.



