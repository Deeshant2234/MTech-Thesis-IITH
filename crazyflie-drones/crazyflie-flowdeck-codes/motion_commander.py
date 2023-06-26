import logging
from pickle import GLOBAL
import sys
import time
from threading import Event
from turtle import pos, position

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper




URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)

DEFAULT_HEIGHT = 0.6
BOX_LIMIT = 0.5

global position_estimate 
position_estimate = [0,0]


def move_box_limit(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        body_x_cmd = 0.2
        body_y_cmd = 0.1
        max_vel = 0.2   #sets the velocity    

        # mc.start_forward(0.6)
        
        while (1):
            # if position_estimate[0] > BOX_LIMIT:
            #    mc.start_back()
            # elif position_estimate[0] < -BOX_LIMIT:
            #    mc.start_forward()

            if position_estimate[0] > BOX_LIMIT:
                body_x_cmd = -max_vel
            elif position_estimate[0] < -BOX_LIMIT:
                body_x_cmd = max_vel
            if position_estimate[1] > BOX_LIMIT:
                body_y_cmd = -max_vel
            elif position_estimate[1] < -BOX_LIMIT:
                body_y_cmd = max_vel

            mc.start_linear_motion(body_x_cmd, body_y_cmd, 0)

            time.sleep(0.1)

def log_pos_callback(timestamp, data, logconf):

    # global position_estimate 
    print(data)
    # position_estimate = [i for i in range(50)]

    position_estimate[0] = data['stateEstimate.x']
    position_estimate[1] = data['stateEstimate.y']
    


def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


def move_linear_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)
        mc.forward(0.5)
        time.sleep(1)
        mc.turn_left(180)
        time.sleep(1)
        mc.forward(0.5)
        # mc.back(0.5)
        time.sleep(1)


def take_off_simple(scf):
    # with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:     #DEFAULT_HEIGHT = 0.3m
    with MotionCommander(scf) as mc:
        mc.up(0.3)  # set the height //0.3m
        time.sleep(3)
        mc.stop()


if __name__ == '__main__':

    cflib.crtp.init_drivers()
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group="deck", name="bcFlow2",
                                    cb=param_deck_flow)
        time.sleep(1)


        logconf = LogConfig(name='Position', period_in_ms=10)
        logconf.add_variable('stateEstimate.x', 'float')
        logconf.add_variable('stateEstimate.y', 'float')
        scf.cf.log.add_config(logconf)
        logconf.data_received_cb.add_callback(log_pos_callback)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        # take_off_simple(scf)
        # move_linear_simple(scf)

        logconf.start()
        # move_linear_simple(scf)
        move_box_limit(scf)
        logconf.stop()
