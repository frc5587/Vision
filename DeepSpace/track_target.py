import cv2
import numpy as np
from math import atan, degrees
import socket
import time

TCP_IP = '10.55.87.2'
TCP_PORT = 3456

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

cap = cv2.VideoCapture(0)
focal_length = 333.82
frame_param = (640, 480)
frame_center = (int(640 / 2), int(480 / 2))
FOV = 86

color_lower = np.array([50, 180, 100])
color_upper = np.array([120, 255, 255])


def get_h_angle(cX):
    return 43 - degrees(atan((frame_param[0] - cX) / focal_length))
    # if(theta > 0):
    #     return 90 - theta
    # elif(theta < 0):
    #     return (-90 - theta)
    # return 0


def get_cnt_center(cnt, frame):
    rect = cv2.minAreaRect(cnt)

    # rect tuple is ( center (x,y), (width, height), angle of rotation ).
    if rect[1][0] < 10:
        return None

    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
    cX, cY = rect[0]

    return rect[0]  # return center point of minAreaRect


def get_midpoint(frame, cnt1, cnt2):
    return (int((cnt1[0] + cnt2[0]) / 2), int((cnt1[1] + cnt2[1]) / 2))


def send_angle(img_cap_time, angle):
    to_send = '{}:{}\n'.format(img_cap_time, round(angle, 3))

    print(to_send)
    s.send(bytearray(to_send, 'utf-8'))


def find_tape():
    _, frame = cap.read()
    cap_time = round(time.time(), 3)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [
        (cv2.contourArea(contours), contours) for contours in contours
    ]

    if len(contour_sizes) > 1:
        maxElement = max(contour_sizes, key=lambda x: x[0])
        biggest_contour = maxElement[1]
        contour_sizes.remove(maxElement)

        next_biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
        cnt1_center = get_cnt_center(biggest_contour, frame)
        cnt2_center = get_cnt_center(next_biggest_contour, frame)

        if cnt1_center is None or cnt2_center is None:
            return

        midpoint = get_midpoint(frame, cnt1_center, cnt2_center)
        send_angle(cap_time, get_h_angle(midpoint[0]))


while True:

    find_tape()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
