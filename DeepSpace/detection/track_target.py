import cv2
import numpy as np
from math import atan, degrees, sqrt
import socket
import time
import os

os.system(
    "uvcdynctrl -s 'Exposure, Auto' 1 && uvcdynctrl -s 'Exposure (Absolute)'" +
    " 0.1 && uvcdynctrl -s 'Brightness' 0.1")

TCP_IP = '10.55.87.2'
TCP_PORT = 3456

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(None)

cap = cv2.VideoCapture(0)
focal_length = 333.82
frame_center = (int(640 / 2), int(480 / 2))
FOV = 86

color_lower = np.array([50, 180, 50])
color_upper = np.array([120, 255, 255])


def connect_tcp():
    while True:
        try:
            s.connect((TCP_IP, TCP_PORT))
            break
        except ConnectionRefusedError:
            print("Could not connect. Waiting one second and trying again...")
            time.sleep(1)


def send_times():
    for i in range(5):
        to_send = '{}\n'.format(round(time.time(), 3))
        print("Sending...")
        s.send(bytearray(to_send, 'utf-8'))


def contour_dist_sort(contour_array):
    cont_centers = []
    distance_center = []

    # Add all contour centers to an array for filtering
    for c in contour_array:
        cnt_center = get_cnt_center(c)

        # if the contour center is None, then return None for both centers
        if cnt_center is not None:
            cont_centers.append(cnt_center)
            distance_center.append(
                get_center_distance(cnt_center, frame_center))

    # Find the smallest distance from frame center to contour center
    d_min_1 = None
    for d in distance_center:
        if d_min_1 is None or d < d_min_1:
            d_min_1 = d

    # If no distance was found, there are no contours
    if d_min_1 is None:
        return (None, None)

    # Find the index of the selected contour to find its center
    d_min_1_pos = distance_center.index(d_min_1)
    closest_center = cont_centers[d_min_1_pos]

    # Remove it from the arrays of interest now that we've seleceted it
    cont_centers.pop(d_min_1_pos)
    distance_center.pop(d_min_1_pos)

    # Find contour with smallest distance from previously selected contour
    d_min_2 = None
    d_min_3 = None
    min_cont_pos = None
    next_cont_pos = None
    for counter, center in enumerate(cont_centers):
        # Get distance from selected contour center to current contour
        cnt_d = get_center_distance(closest_center, center)
        if d_min_2 is None or cnt_d < d_min_2:
            d_min_2 = cnt_d
            min_cont_pos = counter
        elif d_min_3 is None or cnt_d < d_min_3:
            d_min_3 = cnt_d
            next_cont_pos = counter

    # If no distance was found, then there is no second contour
    if d_min_2 is None:
        return (closest_center, None)
    elif d_min_3 is None:
        d_min_3 = d_min_2
        next_cont_pos = min_cont_pos

    # Find the center of the second contour to return it
    next_closest_center = cont_centers[next_cont_pos]

    return (closest_center, next_closest_center)


def get_center_distance(p1, p2):
    return sqrt(((p2[0] - p1[0])**2) + ((p2[1] - p1[1])**2))


def get_h_angle(cX):
    return atan(((int(640 / 2) + .5) - cX) / 333.82)


def get_cnt_center(cnt):
    rect = cv2.minAreaRect(cnt)

    # rect tuple is ( center (x,y), (width, height), angle of rotation ).
    if rect[1][0] < 10:
        return None

    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cX, cY = rect[0]

    return rect[0]  # return center point of minAreaRect


def get_midpoint(cnt1, cnt2):
    return (int((cnt1[0] + cnt2[0]) / 2), int((cnt1[1] + cnt2[1]) / 2))


def find_tape():
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)

    closest_center, next_closest_center = contour_dist_sort(contours)
    if closest_center is None or next_closest_center is None:
        return

    midpoint = get_midpoint(closest_center, next_closest_center)

    to_send = '{}:{}\n'.format(
        round(time.time(), 3), round(degrees(get_h_angle(midpoint[0])), 3))
    print(to_send)
    s.send(bytearray(to_send, 'utf-8'))


if __name__ == "__main__":
    connect_tcp()
    send_times()

    while (True):
        try:
            find_tape()
        except ConnectionResetError or BrokenPipeError:
            s.detach()
            connect_tcp()

    cap.release()
