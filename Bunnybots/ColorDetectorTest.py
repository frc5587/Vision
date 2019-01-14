import cv2
import numpy as np
import math
from decimal import Decimal
import time

cap = cv2.VideoCapture(0)

# Lower color limit for red:
lowerRed = np.array([169, 100, 100])
# Upper color limit for red:
upperRed = np.array([189, 255, 255])
# Lower color limit for blue:
lowerBlue = np.array([95, 100, 100])
# Upper color limit for blue:
upperBlue = np.array([115, 255, 255])

while True:
  # boolean for identified colors
  red = False
  blue = False

  #get frame from video
  _, frame = cap.read()
  start = time.time()

  #get height and width of the video feed frame
  height = np.size(frame, 0)
  width = np.size(frame, 1)

  #switch color space to HSV
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  #Make mask of image, only showing color in between upper and lower color values
  redMask = cv2.inRange(hsv, lowerRed, upperRed)
  blueMask = cv2.inRange(hsv, lowerBlue, upperBlue)

  cv2.imshow("mask", redMask)

  #find contours of colors in respective masks
  im2, redContours, hierarchy = cv2.findContours(
      redMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  im2, blueContours, hierarchy = cv2.findContours(
      blueMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  #get the sizes of all contours
  red_contour_sizes = [(cv2.contourArea(red_contour), red_contour)
                       for red_contour in redContours]
  blue_contour_sizes = [(cv2.contourArea(blue_contour), blue_contour)
                        for blue_contour in blueContours]

  #if there are contorurs, find the biggest one and draw it
  if len(red_contour_sizes) > 0:
    biggest_red_contour = max(red_contour_sizes, key=lambda x: x[0])[1]
    rx, ry, rw, rh = cv2.boundingRect(biggest_red_contour)
    cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), (0, 0, 255), 2)
    red = True

  if len(blue_contour_sizes) > 0:
    biggest_blue_contour = max(blue_contour_sizes, key=lambda x: x[0])[1]
    bx, by, bw, bh = cv2.boundingRect(biggest_blue_contour)
    cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (255, 0, 0), 2)
    blue = True

  #draw black infilled rectangle to overlay text.
  cv2.rectangle(frame, (0, height), (400, height-30), (0, 0, 0), -1)

  #write the color and if it was found in the frame.
  cv2.putText(frame, 'Blue: ' + str(blue), (5, height-15),
              cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 0, 0), 1, cv2.LINE_AA)
  cv2.putText(frame, 'Red: ' + str(red), (100, height-15),
              cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 1, cv2.LINE_AA)

  #display the frame with all overlays and found colors
  cv2.imshow('Show Colors', frame)

  #if the key 'q' is pressed, exit while loop
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

#release the camera
cap.release()
#destroy all existing windows
cv2.destroyAllWindows()
