#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from neato_node.msg import Button
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

# roslib.load_manifest('my_opencv')

class neato_turn:

    def __init__(self):
        rospy.init_node('QR_Nav', anonymous=True)
        rospy.Subscriber("QR", String, self.callback)
        rospy.Subscriber("soft_button", Button, self.bcall)
        rospy.Subscriber("odom", Odometry, self.ocall)
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.pub2 = rospy.Publisher('neato_turn', String, queue_size=1)
        self.state = "Stop"
        self.odom = Odometry()
        self.X = 0
        self.Z = 0
        self.Xo = 0
        self.Zo = 0
        self.old_euler = (0,0,0,0)

    def bcall(self, data):

        if data.value:
            print 'stop'
            self.state = False
            self.callback("test Stop")


    def ocall(self, data):
        twist = Twist()
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0


        # print data
        if self.state == "Turn":
            self.odom = data
            self.old_euler = euler_from_quaternion([data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z,data.pose.pose.orientation.w])
            self.state = "Turning"

        # delta = data.pose.pose.orientation.z-self.odom.pose.pose.orientation.z
        euler = euler_from_quaternion([data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z,data.pose.pose.orientation.w])
        delta = euler[2]-self.old_euler[2]
        if abs(delta) > 3.14:
            delta = abs(delta)-6.28
        if self.state == "Turning":
            if abs(self.Z) >= .3:
                self.Z = self.Z*((1.785-abs(delta))/1.785)
                twist.angular.z = self.Z
                self.pub.publish(twist)
        # print euler[2], self.old_euler[2]

        print euler[2], delta
        if self.state == "Turning" and abs(delta) >= 1.5:
            self.X = self.Xo
            self.Z = self.Zo
            self.pub2.publish('Done')
            self.pub.publish(twist)
            self.callback("test none")
        # print self.odom

    def callback(self, data):
        #rate = rospy.Rate(.5)  # 1/2 hz
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
            self.Xo = self.X
            self.Zo = self.Z
            self.Z = .8
            self.X = 0
            self.state = "Turn"
            self.pub2.publish('Turning')
            #
        elif temp == 'Right':
            self.Xo = self.X
            self.Zo = self.Z
            self.Z = -0.8
            self.X = 0
            self.state = "Turn"
            self.pub2.publish('Turning')
            #self.pub2.publish('Done')
        elif temp == 'Stop':
            print 'Stopping'
            self.X = 0
            self.Z = 0
            self.state = "Stop"
        elif temp == 'Start':
            print 'Starting'
            self.state = "Move"
            self.X = .10
            self.Z = .00825
        elif temp == 'Adjust':
            print 'Adjusting'
            tmp = str(data).split(" ")[2]
            if tmp == "Left":
                th = .05
            if tmp == "Right":
                th = -.05

        twist.angular.z = self.Z+th
        twist.linear.x = self.X
        self.pub.publish(twist)

        return


def navigator():
    neato_turn()
    #rospy.Rate(10)
    rospy.spin()

if __name__ == '__main__':
    navigator()