# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
This script shows the basic use of the MotionCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires some kind of location system, it has been
tested with (and designed for) the flow deck.

The MotionCommander uses velocity setpoints.

Change the URI variable to your Crazyflie configuration.
"""
import logging
import time
import pyrebase
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)
firebaseConfig = {
     "apiKey": "AIzaSyAFNh6SXiDOyShlSGGmHwUYjOx-VilLnZU",
     "authDomain": "connectingfirebasedbtopy-ed362.firebaseapp.com",
     "projectId": "connectingfirebasedbtopy-ed362",
     "storageBucket": "connectingfirebasedbtopy-ed362.appspot.com",
     "databaseURL": "https://connectingfirebasedbtopy-ed362-default-rtdb.firebaseio.com/",
     "messagingSenderId": "302340644641",
     "appId": "1:302340644641:web:a7a0a8b5d707837cc92860",
     "measurementId": "G-642DCYVP5D"
 };
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
state = db.child("IoT_Crazyflie").get()

if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # We take off when the commander is created
           if state.val()["Command"] =='"take off"':
                with MotionCommander(scf) as mc:
                    time.sleep(1)
                    while state.val()["Command"] =='"take off"':  
                            print("Drone is Hovering")
                            state = db.child("IoT_Crazyflie").get()
                            if state.val()["Command"] !='"take off"':
                                break
                    while True:
                            while state.val()["Command"] =='"take off"':  
                                print("Drone is Hovering")
                                mc.up(0.5)
                                state = db.child("IoT_Crazyflie").get()
                                if state.val()["Command"] !='"take off"':
                                    break 
                        # There is a set of functions that move a specific distance
                        # We can move in all directions
                            state = db.child("IoT_Crazyflie").get()
                            while state.val()["Command"] =='"forward"':
                                mc.forward(0.5)
                                state = db.child("IoT_Crazyflie").get()
                                if state.val()["Command"] !='"forward"':
                                    break
                        
                            state = db.child("IoT_Crazyflie").get()
                            while state.val()["Command"] =='"backward"':
                                state = db.child("IoT_Crazyflie").get()
                                mc.back(0.5)
                                if state.val()["Command"] !='"backward"':
                                    break
                            
                            state = db.child("IoT_Crazyflie").get()
                            while state.val()["Command"] =='"land"':
                                state = db.child("IoT_Crazyflie").get()
                                mc.land(0.3)
                                if state.val()["Command"] !='"land"':
                                    break
                            
                            state = db.child("IoT_Crazyflie").get()
                            while state.val()["Command"] =='"circle"':
                                state = db.child("IoT_Crazyflie").get()
                                mc.circle_right(0.5, velocity=0.5, angle_degrees=180)
                                if state.val()["Command"] !='"circle"':
                                    break

                    # We land when the MotionCommander goes out of scope
