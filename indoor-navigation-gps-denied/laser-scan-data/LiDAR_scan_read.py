#!/usr/bin/python3

import rospy
from sensor_msgs.msg import LaserScan

def callback(msg):
    #print(len(msg.ranges))
    print('Front Distance(in m):')
    print(msg.ranges[0])
    print('Left Distance(in m):')
    print(msg.ranges[52])
    print('Back Distance(in m):')
    print(msg.ranges[105])
    print('Right Distance(in m):')
    print(msg.ranges[157])

if __name__ == '__main__':
    rospy.init_node('scan_values')
    sub = rospy.Subscriber('/scan', LaserScan, callback)
    rospy.spin()
