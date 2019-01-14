import cv2
import numpy as np
from math import atan, degrees

cap = cv2.VideoCapture(1)
focal_length = 333.82
frame_param = (640,480)
frame_center = (int(640/2), int(480/2))
FOV = 86

def get_h_angle(cX):
    h_angle = degrees(atan((frame_param[0] - cX) / focal_length))
    return int(43 - h_angle)


def get_cnt_center(cnt, frame):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
    cX,cY = rect[0]
    # cv2.circle(frame, (int(cX), int(cY)), 10, (255, 0, 0), -1)

    return rect[0]  # return center point of minAreaRect
    # cv2.contourArea(box)


def get_midpoint(frame, cnt1, cnt2):
    # cv2.circle(frame, (int(cnt1[0]) ,int(cnt1[1])) , 10, (255, 0, 0), -1)
    # cv2.circle(frame, (int(cnt2[0]),int(cnt2[1])) , 10, (255, 0, 0), -1)
    return (int((cnt1[0] + cnt2[0])/2), int((cnt1[1]+cnt2[1])/2))


def find_tape():
    #sticky note orange:
    color_lower = np.array([0, 118, 131])
    color_upper = np.array([25, 225, 255])

    # Logo blue:
    # color_lower = np.array([94, 78, 46])
    # color_upper = np.array([129, 187, 255])

    # Retro green:
    # color_lower = np.array([35, 0, 216])
    # color_upper = np.array([47, 2, 255])

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
            cv2.rectangle(frame, (0, frame_param[0]), (450, int(frame_param[1] - 25)), (0, 0, 0), -1)
            cv2.putText(frame, 'Horizontal Angle to Target (degrees): ' + str(get_h_angle(midpoint[0])),
                (5, frame_param[1]-10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow("Frame", frame)


while(True):

    find_tape()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
