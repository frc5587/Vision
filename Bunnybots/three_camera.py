import cv2
from networktables import NetworkTables
import numpy as np

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
sd = NetworkTables.getTable("SmartDashboard")

cameras = [
    cv2.VideoCapture(0),
    cv2.VideoCapture(1),
    cv2.VideoCapture(2)
]

#Lower color limits
red = ([169, 100, 100], [189, 255, 255])
blue = ([95, 100, 100], [115, 255, 255])


def color_found(cam, color_bounds):
    frame = cam.read()[1]

    color_lower = np.array(color_bounds[0], dtype="uint8")
    color_upper = np.array(color_bounds[1], dtype="uint8")

    #switch color space to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Make mask of image, only showing color in between upper and lower color values
    mask = cv2.inRange(hsv, color_lower, color_upper)

    #find contours of colors in respective masks
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #get the sizes of all contours
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]

    #if there are contorurs, find the biggest one and draw it
    return len(contour_sizes) > 0


while True:
    for cam_num, cam in enumerate(cameras):
        is_red = color_found(cam, red)
        is_blue = color_found(cam, blue)

        sd.putBoolean("Camera " + str(cam_num) + " Red", is_red)
        sd.putBoolean("Camera " + str(cam_num) + " Blue", is_red)

        print("Cam" + str(cam_num) + " - Red: " + str(is_red) + " | Blue: " + str(is_blue))

# Runs if while loop is exited
for cam in cameras:
    cam.release()