#!/usr/bin/env python
from flask import Flask, request, redirect
import twilio.twiml
import pifacedigitalio as pfio
from time import sleep
from datetime import datetime
import json

with open('/doorman/building_admins.json') as a:
    building_admins = json.load(a)

with open('/doorman/participants.json') as p:
    participants = json.load(p)

pfio.init()

def unlock_gate():
    pfio.digital_write(0,1)
    sleep(1)
    pfio.digital_write(0,0)
    sleep(1)

def office_hours():
    hour = datetime.now().hour
    day = datetime.now().weekday()
    #Time is host time and day is 0 - 6 for Monday - Sunday
    if 5 < hour < 18 and day < 5:
        return True
    else:
        return False

app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def open_or_not():
    # Get the phone number from the incoming Twilio request
    from_number = request.values.get('From', None)
    resp = twilio.twiml.Response()

    # if a building admin calls, always unlock:
    if from_number in building_admins:
        unlock_gate()
        resp.say("Welcome " + building_admins[from_number] + " come inside")
    # if a participant calls during office hours, unlock
    elif from_number in participants and office_hours() == True:
        unlock_gate()
        resp.say("Welcome " + participants[from_number] + " welcome back")
    # if a participant calls outside of office hours, do not unlock
    elif from_number in participants and office_hours() == False:
        resp.say("sorry " + participants[from_number] + " it is outside of office hours")
        resp.say("I'm sorry " + participants[from_number] + " it is outside of office hours")
    # for any caller not on the lists, do not unlock
    else:
        resp.say("I'm sorry, I do not know you so I may not unlock.")

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6789, debug=False)
