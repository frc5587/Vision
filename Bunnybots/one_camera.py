import cv2
from networktables import NetworkTables
import numpy as np

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

ip = "10.55.87.2"
NetworkTables.initialize(server=ip)
sd = NetworkTables.getTable("SmartDashboard")

cam = cv2.VideoCapture(0)

# Lower color limits
red = ([160, 100, 100], [179, 255, 255])
blue = ([95, 100, 100], [115, 255, 255])


def color_found(cam, color_bounds):
    frame = cam.read()[1]

    color_lower = np.array(color_bounds[0], dtype="uint8")
    color_upper = np.array(color_bounds[1], dtype="uint8")

    # switch color space to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Make mask of image, only showing color in between upper
    # and lower color values
    mask = cv2.inRange(hsv, color_lower, color_upper)

    # find contours of colors in respective masks
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)

    if (len(contours) > 0):
        biggest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest_contour)
        if w > 10.0:
            return y + int(
                h / 2)  # distance from the top of the frame to center of ball
    return 0


while True:
    red_distance = color_found(cam, red)
    blue_distance = color_found(cam, blue)
    print(red_distance, blue_distance)

    if red_distance > blue_distance:
        ball_color = "Red"
    elif blue_distance > red_distance:
        ball_color = "Blue"
    else:
        ball_color = "None"

    sd.putString("Color", ball_color)

    print("Closest Ball: " + ball_color)

# Runs if while loop is exited
cam.release()
