#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
# roslib.load_manifest('my_opencv')

class neato_turn:

    def __init__(self):
        rospy.init_node('QR_Nav', anonymous=True)
        rospy.Subscriber("QR", String, self.callback)
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.pub2 = rospy.Publisher('neato_turn', String, queue_size=1)
        self.state = False


    def callback(self, data):
        rate = rospy.Rate(.5)  # 1/2 hz
        twist = Twist()
        temp = str(data).split(" ")[1]
        th = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0

        if temp == 'Left':
            twist.angular.z = .825
            self.pub2.publish('Turning')
            self.pub.publish(twist)
            rate.sleep()
            self.pub2.publish('Done')
        elif temp == 'Right':
            twist.angular.z = -0.79
            self.pub2.publish('Turning')
            self.pub.publish(twist)
            rate.sleep()
            self.pub2.publish('Done')
        elif temp == 'Stop':
            print 'Stopping'
            self.pub.publish(twist)
            self.state = False
        elif temp == 'Start':
            print 'Starting'
            self.state = True
        elif temp == 'Adjust':
            print 'Adjusting'
            if temp[2] == "Left":
                th = .01
            if temp[2] == "Right":
                th = -.01

        if self.state:
            twist.angular.z = .00825+th
            twist.linear.x = .10
            self.pub.publish(twist)

        return


def navigator():
    neato_turn()
    rospy.spin()

if __name__ == '__main__':
    navigator()