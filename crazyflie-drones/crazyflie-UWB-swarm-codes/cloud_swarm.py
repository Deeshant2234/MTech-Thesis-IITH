# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2017-2018 Bitcraze AB
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
Version of the AutonomousSequence.py example connecting to 10 Crazyflies.
The Crazyflies go straight up, hover a while and land but the code is fairly
generic and each Crazyflie has its own sequence of setpoints that it files
to.

The layout of the positions:
    x2      x1      x0

y3  10              4

            ^ Y
            |
y2  9       6       3
            |
            +------> X

y1  8       5       2



y0  7               

"""
import time
import pyrebase
import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
import math

# Change uris and sequences according to your setup
URI6 = 'radio://0/60/2M/E7E7E7E706'
URI5 = 'radio://0/10/2M/E7E7E7E701'
URI3 = 'radio://0/30/2M/E7E7E7E703'
URI2 = 'radio://0/40/2M/E7E7E7E704'

firebaseConfig = {
    "apiKey": "AIzaSyAFNh6SXiDOyShlSGGmHwUYjOx-VilLnZU",
    "authDomain": "connectingfirebasedbtopy-ed362.firebaseapp.com",
    "projectId": "connectingfirebasedbtopy-ed362",
    "storageBucket": "connectingfirebasedbtopy-ed362.appspot.com",
    "databaseURL": "https://connectingfirebasedbtopy-ed362-default-rtdb.firebaseio.com/",
    "messagingSenderId": "302340644641",
    "appId": "1:302340644641:web:a7a0a8b5d707837cc92860",
    "measurementId": "G-642DCYVP5D"
}
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
state = db.child("IoT_Crazyflie").get()


z0 = 1.5
z = 2.5
z2 = 0.5

x0 = 1.0
x1 = 0
x2 = -0.7


y0 = -1.8
y1 = -0.6
y2 = 0.6
y3 = 1.0

#    x   y   z  time

sequence2 = [
    (x0, y1, z0, 3.0),
    (x0, y1, z, 10.0),
    (x0, y1, z0, 3.0),

]

sequence3 = [
    (x0, y2, z0, 3.0),
    (x0, y2, z, 10.0),
    (x0, y2, z0, 3.0),
]

sequence4 = [
    (x1, y0, z0, 3.0),
    (x1, y0, z, 10.0),
    (x1, y0, z0, 3.0),
]

sequence5 = [
    (x1, y1, z0, 3.0),
    (x1, y1, z, 10.0),
    (x1, y1, z0, 3.0),
]

sequence6 = [
    (x1, y2, z0, 3.0),
    (x1, y2, z, 10.0),
    (x1, y2, z0, 3.0),
]


seq_args = {
    
    URI6: [sequence6],
    URI5: [sequence5],
    URI3: [sequence3],
    URI2: [sequence2],
}

# List of URIs, comment the one you do not want to fly
uris = { 
    URI6,
    URI5,
    URI3,
    URI2,
}


def wait_for_param_download(scf):
    while not scf.cf.param.is_updated:
        time.sleep(1.0)
    print('Parameters downloaded for', scf.cf.link_uri)


def take_off(cf, position):
    take_off_time = 1.0
    sleep_time = 0.1
    steps = int(take_off_time / sleep_time)
    vz = position[2] / take_off_time

    print(vz)

    for i in range(steps):
        cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
        time.sleep(sleep_time)


def land(cf, position):
    landing_time = 1.0
    sleep_time = 0.1
    steps = int(landing_time / sleep_time)
    vz = -position[2] / landing_time

    print(vz)

    for _ in range(steps):
        cf.commander.send_velocity_world_setpoint(0, 0, vz, 0)
        time.sleep(sleep_time)

    cf.commander.send_stop_setpoint()
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)

def poshold(cf, t, z):
    steps = t * 10

    for r in range(steps):
        cf.commander.send_hover_setpoint(0, 0, 0, z) 
        time.sleep(0.1)

def run_sequence1(scf, seq_args):
    cf = scf.cf

    # Number of setpoints sent per second
    fs = 4
    fsi = 1.0 / fs

    # Compensation for unknown error :-(
    comp = 1.3

    # Base altitude in meters
    base = 0.5

    d = 0.8
    z = 2.5

    poshold(cf, 2, base)

    ramp = fs * 2
    for r in range(ramp):
        cf.commander.send_hover_setpoint(0, 0, 0, base + r * (z - base) / ramp)
        time.sleep(fsi)

    poshold(cf, 2, z)

    for _ in range(2):
        # The time for one revolution
        circle_time = 5

        steps = circle_time * fs
        for _ in range(steps):
            cf.commander.send_hover_setpoint(d * comp * math.pi / circle_time,
                                             0, 360.0 / circle_time, z)
            time.sleep(fsi)

    poshold(cf, 2, z)

    for r in range(ramp):
        cf.commander.send_hover_setpoint(0, 0, 0,
                                         base + (ramp - r) * (z - base) / ramp)
        time.sleep(fsi)

    poshold(cf, 1, base)

    cf.commander.send_stop_setpoint()

def run_sequence2(scf, sequence):
    
    # Number of setpoints sent per second
    fs = 4
    fsi = 1.0 / fs

    # Compensation for unknown error :-(
    comp = 1.3

    # Base altitude in meters
    base = 0.5

    d = 0.8
    z = 2.5    
    
    try:
        cf = scf.cf

        while True:
            state = db.child("IoT_Crazyflie").get()
            if state.val()["Command"] == '"take off"':
                break

        take_off(cf, sequence[0])
     
        for position in sequence:
            print('Setting position {}'.format(position))
            end_time = time.time() + position[3]
            state = db.child("IoT_Crazyflie").get()
            while (time.time() < end_time) or (state.val()["Command"] == '"position hold"'):
                cf.commander.send_position_setpoint(position[0],
                                                    position[1],
                                                    position[2], 0)
                time.sleep(0.1)
                state = db.child("IoT_Crazyflie").get()
                if state.val()["Command"] == '"land"':
                    break
            state = db.child("IoT_Crazyflie").get()
            while state.val()["Command"] == '"circle"':
                for _ in range(1):
                    # The time for one revolution
                    circle_time = 5
                    steps = circle_time * fs
                    for _ in range(steps):
                        cf.commander.send_hover_setpoint(d * comp * math.pi / circle_time,
                                                        0, 360.0 / circle_time, position[2])
                        time.sleep(fsi)
                state = db.child("IoT_Crazyflie").get()
                if state.val()["Command"] != '"circle"':
                    break

            state = db.child("IoT_Crazyflie").get()
            if state.val()["Command"] == '"land"':
                break
            state = db.child("IoT_Crazyflie").get()
        land(cf, sequence[-1])

    except Exception as e:
        print(e)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        # If the copters are started in their correct positions this is
        # probably not needed. The Kalman filter will have time to converge
        # any way since it takes a while to start them all up and connect. We
        # keep the code here to illustrate how to do it.
        # swarm.reset_estimators()

        # The current values of all parameters are downloaded as a part of the
        # connections sequence. Since we have 10 copters this is clogging up
        # communication and we have to wait for it to finish before we start
        # flying.
        print('Waiting for parameters to be downloaded...')
        swarm.parallel(wait_for_param_download)
        swarm.parallel(run_sequence2, args_dict=seq_args)
