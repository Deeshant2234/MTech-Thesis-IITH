#! /usr/bin/env python3
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import rospy
from sensor_msgs.msg import LaserScan

global laser_msg
global front_laser
global left_laser
global right_laser
global back_laser
left_l = []
connection_string = "/dev/ttyACM0"
vehicle = connect(connection_string, wait_ready=True)
gnd_speed = 0.5 #fm/s 

#-- Define the function for sending mavlink velocity command in body frames 
def set_velocity_body(vehicle,vx,vy,vz):
    """remember vz is positive downward"""
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0,0,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b000111000111,
        0,0,0,
        vx,vy,vz,
        0,0,0,
        0,0)    #0.2
    vehicle.send_mavlink(msg)
    vehicle.flush()
def set_position_body(vehicle,px,py,pz):
    """remember vz is positive downward"""
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0,0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b100111111000,
        px,py,pz,
        0,0,0,
        0,0,0,
        0,0 )
    vehicle.send_mavlink(msg)
    vehicle.flush()

def left(vehicle,gnd_speed):
    set_velocity_body(vehicle,0,-gnd_speed,0)
    time.sleep(0.5)
    
      
def right(vehicle,gnd_speed):
    set_velocity_body(vehicle,0,gnd_speed,0)
    time.sleep(0.5)
    
    
def forward(vehicle,gnd_speed):
    set_velocity_body(vehicle,gnd_speed,0,0)
    time.sleep(0.5)
    
def backward(vehicle,gnd_speed):
    set_velocity_body(vehicle,-gnd_speed,0,0)
    time.sleep(0.5)

def hover(vehicle):
    set_velocity_body(vehicle,0,0,0)
    time.sleep(0.5) 

def callback(msg):
    #print(len(msg.ranges))

    global laser_msg, front_laser, left_laser, back_laser, right_laser, left_l
    
    
     
    laser_msg = msg.ranges
    front_laser = msg.ranges[0]
    left_laser = msg.ranges[52]
    back_laser = msg.ranges[105]
    right_laser = msg.ranges[157]  
    if(((left_laser<=3)and(left_laser>=0.12))):
        print("moving right")
        #right(vehicle,gnd_speed)
        #time.sleep(2.5)
        #vehicle.mode= VehicleMode("LAND")
    
    if(((right_laser<=3)and(right_laser>=0.12))):
        print("moving left")
        #left(vehicle,gnd_speed)
        #time.sleep(2.5)

    # if(((left_laser>3)or(left_laser<0.09))):
    #     print("hover")
    #     #time.sleep(2.5)
    #     print("hover")
    #     #time.sleep(2.5)
    #print(f"left messages : {left_laser}")
    #print(f"right messages : {right_laser}")
    if(((left_laser>3)or(left_laser<0.09))and((right_laser>3)or(right_laser<0.09))):
        print("hover")
        # time.sleep(2.5)
        print("hover")
        # time.sleep(2.5)

'''
    print(msg.ranges[0]'front')
    print(msg.ranges[52]'left')
    print(msg.ranges[105]'back')
    print(msg.ranges[157]'right')
'''

# -- Define the function for takeoff
def arm_and_takeoff(tgt_altitude):
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    #while not vehicle.is_armable:
     #   time.sleep(1)
    vehicle.armed = True

    while not vehicle.armed:
        time.sleep(2)
        vehicle.armed=True   
    print("Takeoff")
    vehicle.simple_takeoff(tgt_altitude)

    # -- wait to reach the target altitude
    while True:
        altitude = vehicle.location.global_relative_frame.alt

        if altitude >= tgt_altitude - 1:
            print("Altitude reached")
            break

        time.sleep(1)


# ------ MAIN PROGRAM ----

if __name__ == "__main__":
    rospy.init_node('scan_values')
 #   print("below scan vau")
    #app.run(host='0.0.0.0', port=5000, debug=True)
    #arm_and_takeoff(2)
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()


