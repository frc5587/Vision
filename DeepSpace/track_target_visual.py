import cv2
import numpy as np
from math import atan, tan, radians, degrees
import socket
import time

# TCP_IP = '10.55.87.2'
# TCP_PORT = 3456

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((TCP_IP, TCP_PORT))
# distance between cameras = 10.75 in
# f = (P x d) /w
# d = (w x f) / p

cap = cv2.VideoCapture(1)
focal_length = 333.82
frame_center = (int(640/2), int(480/2))
FOV = 86

camera_height = (3*12)+9.5
camera_offset_angle = radians(-30)
target_height = 29.25

diff_height = camera_height - target_height


def get_y_distance(cY):
    if((frame_center[1] - cY) > 0):
        # Vertical Angle to Target
        theta = atan((frame_center[1] - cY)/focal_length)
        v_compound_angle = theta + camera_offset_angle
        print(str(degrees(theta)))
        return diff_height/tan(v_compound_angle)
    return 0


def get_x_distance(cX, setpoint_y):
    if((frame_center[0] - cX) > 0 and setpoint_y > 0):
        h_angle_to_target = ((frame_center[0] - cX) / focal_length)
        return (((frame_center[0] - cX) / focal_length) * setpoint_y)
    return 0


def get_cnt_center(cnt, frame):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
    cX, cY = rect[0]
    cv2.circle(frame, (int(cX), int(cY)), 10, (255, 0, 0), -1)

    return rect[0]  # return center point of minAreaRect


def get_midpoint(frame, cnt1, cnt2):
    return (int((cnt1[0] + cnt2[0])/2), int((cnt1[1]+cnt2[1])/2))


def find_contour():
    #sticky note orange:
    # color_lower = np.array([0, 118, 131])
    # color_upper = np.array([25, 225, 255])

    # Logo blue:
    # color_lower = np.array([94, 78, 46])
    # color_upper = np.array([129, 187, 255])

    # Retro green:
    color_lower = np.array([35, 0, 216])
    color_upper = np.array([47, 2, 255])

    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    _, contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contours), contours)
                     for contours in contours]
    cv2.circle(frame, frame_center, 10, (0, 255, 0), -1)
    if(len(contour_sizes) > 0):
        maxElement = max(contour_sizes, key=lambda x: x[0])
        biggest_contour = maxElement[1]
        contour_sizes.remove(maxElement)
        if(len(contour_sizes) > 0):
            next_biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
            cnt1_center = get_cnt_center(biggest_contour, frame)
            cnt2_center = get_cnt_center(next_biggest_contour, frame)

            midpoint = get_midpoint(frame, cnt1_center, cnt2_center)
            cv2.circle(frame, midpoint, 10, (255, 0, 0), -1)

            setpoint_y = get_y_distance(midpoint[1])
            setpoint_x = get_x_distance(midpoint[0], setpoint_y)

            setpoint = (setpoint_x, setpoint_y)
            print(str(setpoint))

            # print(" D: " + str(get_distance(midpoint[1])))
            # cv2.rectangle(frame, (0, frame_param[0]), (450, int(frame_param[1] - 25)), (0, 0, 0), -1)
            # to_send = '{}:{}\n'.format(round(time.time(),3), round(get_h_angle(midpoint[0]),3))
            # print("Sending...")
            # s.send(bytearray(to_send, 'utf-8'))
    cv2.imshow("Frame", frame)


while(True):

    find_contour()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
