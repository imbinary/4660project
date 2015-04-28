#!/usr/bin/env python
import roslib
roslib.load_manifest('my_opencv')
import sys
import rospy
import cv2
import zbar
import math
from PIL import Image as Image2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import String


class qr_reader:

    def __init__(self):
        rospy.init_node('qr_reader', anonymous=True)
        self.image_pub = rospy.Publisher("image_topic_2", Image, queue_size=10)
        self.qr_pub = rospy.Publisher('QR', String, queue_size=1)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("camera/image_raw", Image, self.callback)
        self.turn_sub = rospy.Subscriber("neato_turn", String, self.turnback)
        self.sendqr = True
        self.threshold = 10
        self.adjusting = False

    def turnback(self, data):
        tmp = str(data).split(" ")[1]
        if tmp == "Turning":
            print "turn"
            self.sendqr = False
        if tmp == "Done":
            print "done"
            self.sendqr = True


    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            imgray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

             # create a reader
            scanner = zbar.ImageScanner()

            # configure the reader
            scanner.parse_config('enable')

            pil = Image2.fromarray(imgray)
            width, height = pil.size
            raw = pil.tostring()

            # wrap image data
            image = zbar.Image(width, height, 'Y800', raw)

            # scan the image for barcodes
            scanner.scan(image)
            # extract results
            for symbol in image:
                # do something useful with results
                if symbol.data == "None":
                    print "error"
                else:
                    if self.sendqr:
                        [a,b,c,d] = symbol.location   # it returns the four corners of the QR code in an order
                        w = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)  # Just distance between two points
                        th = 320 - ((d[0]+a[0])/2)
                        print th
                        if abs(th) > self.threshold:
                            self.adjusting = True
                            if th > 0:
                                self.qr_pub.publish("Adjust Left")
                            else:
                                self.qr_pub.publish("Adjust Right")
                        elif self.adjusting:
                            self.qr_pub.publish("Adjust Straight")
                            self.adjusting = False

                        if w > 130:
                            qrdata = symbol.data
                            self.qr_pub.publish(qrdata)
                            print qrdata
                        cv2.rectangle(cv_image, a, c, (255, 0, 0), 2)

        except CvBridgeError, e:
            print e

        try:

            self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))

        except CvBridgeError, e:
             print e


def main(args):
    qr_reader()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down"

if __name__ == '__main__':
    main(sys.argv)
