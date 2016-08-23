#! /usr/bin/env python

import cv2
import numpy as np

color_tracker_window = "Color Tracker"


class ColorTracker:

    def __init__(self):
        # cv2.NamedWindow( color_tracker_window, 1 )
        self.capture = cv2.VideoCapture(0)

    def run(self):
        while True:
            _, img = self.capture.read()

            # blur the source image to reduce color noise
            blur = cv2.GaussianBlur(img, (1, 1), 0)

            # convert the image to hsv(Hue, Saturation, Value) so its
            # easier to determine the color to track(hue)
            hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

            # limit all pixels that don't match our criteria, in this case we
            # are looking for purple but if you want you can adjust the first
            # value in both turples which is the hue range(120,140).  OpenCV
            # uses 0-180 as a hue range for the HSV color model
            lower_blue = np.array([296, 54, 80])
            upper_blue = np.array([338, 100, 100])
            thresholded_img = cv2.inRange(hsv_img, lower_blue, upper_blue)

            # determine the objects moments and check that the area is large
            # enough to be our object
            moments = cv2.moments(thresholded_img)
            area = moments['m00']

            # there can be noise in the video so ignore objects with small areas
            if(area > 10000):
                # determine the x and y coordinates of the center of the object
                # we are tracking by dividing the 1, 0 and 0, 1 moments by the
                # area
                x = int(moments['m10']/area)
                y = int(moments['m01']/area)

                print 'x: ' + str(x) + ' y: ' + str(y) + ' area: ' + str(area)

                # create an overlay to mark the center of the tracked object
                overlay = hsv_img

                cv2.circle(overlay, (x, y), 2, (255, 255, 255), 20)
                img2 = np.copy(img)
                cv2.add(img, overlay, img2)
                # add the thresholded image back to the img so we can see what
                # was left after it was applied
                cv2.merge(thresholded_img, img2)

            # display the image
            cv2.imshow(color_tracker_window, img2)
            cv2.imshow(color_tracker_window+"raw", img)
            cv2.imshow(color_tracker_window+"thresholded", thresholded_img)

            if cv2.waitKey(10) == 27:
                break

if __name__ == "__main__":
    color_tracker = ColorTracker()
    color_tracker.run()
