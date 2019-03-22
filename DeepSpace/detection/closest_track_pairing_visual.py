import cv2
import numpy as np
from math import atan, degrees, sqrt
from random import randint
from imutils.video import FPS
# import socket
import time
import os

os.system(
    "uvcdynctrl -s 'Exposure, Auto' 1 && uvcdynctrl -s 'Exposure (Absolute)'" +
    " 0.1 && uvcdynctrl -s 'Brightness' 0.1")

# TCP_IP = '10.55.87.2'
# TCP_PORT = 3456

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.settimeout(None)

CAP = cv2.VideoCapture(0)
FOCAL_LENGTH = 333.82
FRAME_CENTER = (int(640 / 2), int(480 / 2))
FOV = 86

ANGLE_TOLERANCE_DEG = 2

# Green
color_lower = np.array([50, 180, 50])
color_upper = np.array([120, 255, 255])

# Blue
# color_lower = np.array([100, 180, 50])
# color_upper = np.array([140, 255, 255])

last_pos = None

# def connect_tcp():
#     while True:
#         try:
#             s.connect((TCP_IP, TCP_PORT))
#             break
#         except ConnectionRefusedError:
#             print("Could not connect. Waiting one sec and trying again...")
#             time.sleep(1)

# def send_times():
#     for i in range(5):
#         to_send = '{}\n'.format(round(time.time(), 3))
#         print("Sending...")
#         s.send(bytearray(to_send, 'utf-8'))


def get_pair_rects(frame, contours):
    """Get all valid pairs of tape in rect form given a list of OpenCV contours.

    Using the angles and center coordinates associated with each of the
    contours, possible pairs of tape are identified. However, there is no
    verification done to ensure that contours are valid pieces of tape, as the
    function assumes that they are valid.

    If no valid pairs are detected in the given list of contours, an empty
    list is returned in place of a list that ressembles
    [(rect1, rect2), (rect3, rect4), ... ]

    Arguments:
        frame {image} -- the image the contours were taken from (for drawing)
        countours {list} -- list/numpy array of all of the contours
                            in a given frame

    Returns:
        list -- list of tuples comprised of two rects each, where each rect is
                the minAreaRect for a contour
    """

    rect_pairs = []
    for index, cnt in enumerate(contours):
        # Rotated rect - ( center (x,y), (width, height), angle of rotation )
        rect = cv2.minAreaRect(cnt)
        center_x, center_y = rect[0]
        rect_angle = -round(rect[2], 2)

        cv2.putText(frame, str(rect_angle), (int(center_x), int(center_y)),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if rect_angle > 45.0:
            # Iterate through all of the potential matches
            min_x_dist = min_rect = min_index = None
            for pot_index, pot_match in enumerate(contours):
                if np.array_equal(pot_match, cnt):
                    continue

                match_rect = cv2.minAreaRect(pot_match)

                # Check if match is to the right of the contour
                if match_rect[0][0] > rect[0][0] and abs(
                        match_rect[2] - rect_angle) > ANGLE_TOLERANCE_DEG:
                    x_distance = match_rect[0][0] - rect[0][0]

                    if min_x_dist is None or x_distance < min_x_dist:
                        min_x_dist = x_distance
                        min_rect = match_rect
                        min_index = pot_index

            if min_rect is not None:
                rect_pairs.append((rect, min_rect))
                np.delete(contours, index)
                np.delete(contours, min_index)

    for rects in rect_pairs:
        color = (randint(128, 255), randint(128, 255), randint(128, 255))

        for rect in rects:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.line(frame, tuple(box[0]), tuple(box[-1]), (0, 255, 0), 3)
            cv2.drawContours(frame, [box], 0, tuple(color), 2)

    return rect_pairs


def get_pairs(rects, frame):
    rect_pairs = []
    for index, rect in enumerate(rects):
        # Rotated rect - ( center (x,y), (width, height), angle of rotation )
        center_x, center_y = rect[0]
        rect_angle = -round(rect[2], 2)

        if rect_angle > 45.0:
            # Iterate through all of the potential matches
            min_x_dist = min_rect = None
            # min_x_dist = min_rect = min_index = None
            for pot_index, match_rect in enumerate(rects):
                # Check if match is to the right of the contour
                if match_rect[0][0] > rect[0][0] and abs(
                        match_rect[2] - rect_angle) > ANGLE_TOLERANCE_DEG:
                    x_distance = match_rect[0][0] - rect[0][0]

                    if min_x_dist is None or x_distance < min_x_dist:
                        min_x_dist = x_distance
                        min_rect = match_rect
                        # min_index = pot_index

            if min_rect is not None:
                rect_pairs.append((rect, min_rect))
                # np.delete(rects, index)
                # np.delete(rects, min_index)

        if index > 4:
            break

    for pair in rect_pairs:
        color = (randint(128, 255), randint(128, 255), randint(128, 255))

        for rect in pair:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.line(frame, tuple(box[0]), tuple(box[-1]), (0, 255, 0), 3)
            cv2.drawContours(frame, [box], 0, tuple(color), 2)

    return rect_pairs


def get_rects_by_height(contours):
    rects = []
    for cont in contours:
        rect = cv2.minAreaRect(cont)

        if rect[1][0] <= 25.0 or rect[1][1] <= 25.0:
            continue

        rects.append(rect)

    rects.sort(key=lambda rect: rect[1][1], reverse=True)
    return rects


def find_pair_centers(frame, rect_pairs):
    """Find all of the pair centers given a list of pairs of rotated rectangles.

    The function iterates through a list of pairs of rotated rectangles,
    storing the center of each pair in a list to be returned by the function,
    in which the indexes between a pair and its center match up. If the
    rect_pairs list is empty, an empty list of centers is returned.

    Arguments:
        frame {image} -- image to draw the centers of pairs on
        rect_pairs {list} -- list of pairs of rotated rectangles

    Returns:
        list -- centers found from the list of rotated rect pairs
    """

    centers = []
    for rect1, rect2 in rect_pairs:
        center = midpoint(frame, rect1[0], rect2[0])
        centers.append(center)

    return centers


def closest_to_point(frame, rect_pairs, point):
    centers = find_pair_centers(frame, rect_pairs)

    min_dist = min_center = None
    for center in centers:
        dist = distance(center, point)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_center = center

    cv2.circle(frame, min_center, 10, (0, 0, 255), -1)
    return min_center


def closest_center(frame, rect_pairs):
    """Gets the center of the rectangle pair closest to the center of the frame.

    Iterates through the rotated rectangle pairs, finding the rect pair that
    is closest to the center of the frame and then returning the center point
    of that rect pair or None if the rect_pairs list is empty. This function,
    however, does not detect center point of the provided frame, but uses the
    global FRAME_CENTER variable in this script.

    Arguments:
        frame {image} -- the image on which to draw the centers of rect pairs
        rect_pairs {list} -- list of pairs of rotated rectangles

    Returns:
        tuple[int, int] or None -- the coordinates of the center of the rect
                                   pair closest to the center of the frame
    """
    return closest_to_point(frame, rect_pairs, FRAME_CENTER)


def distance(p1, p2):
    """Calculate the distance between two points.

    Arguments:
        p1 {tuple[int, int]} -- the first point to use to find distance
        p2 {tuple[int, int]} -- the second point to use to find distance

    Returns:
        float -- the distance between p1 and p2
    """

    return sqrt(((p2[0] - p1[0])**2) + ((p2[1] - p1[1])**2))


def horizontal_angle(cX):
    """Find the angle between cX and the center of the frame.

    Arguments:
        cX {int} -- the x coordinate to find the angle for

    Returns:
        float -- the angle between cX and the frame center in radians
    """

    return atan(((FRAME_CENTER[0] + .5) - cX) / FOCAL_LENGTH)


def midpoint(frame, point1, point2):
    """Find the midpoint between point1 and point2.

    Arguments:
        frame {image} -- the image to draw the midpoint on
        point1 {tuple[int, int]} -- the first point
        point2 {tuple[int, int]} -- the second point

    Returns:
        tuple[int, int] -- the coordinates of the midpoint
    """

    x, y = (int((point1[0] + point2[0]) / 2), int((point1[1] + point2[1]) / 2))
    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    return (x, y)


def find_tape():
    """Find the tape using the VideoCapture object in this script and display it.

    Fetches a frame from the CAP object in this script and finds the
    horizontal angle between the center of the frame and the tape pair closest
    to the center of the frame. It prints the horizontal angle and draws
    various information on the frame before displaying it in a window.
    """

    global last_pos

    _, frame = CAP.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Find all valid pair rects, and reutrn if none found
    # pair_rects = get_pair_rects(frame, contours)
    rects = get_rects_by_height(contours)
    pair_rects = get_pairs(rects, frame)
    if len(pair_rects) == 0:
        return

    # If found, continue on and post results
    center = None
    if last_pos is None:
        center = closest_center(frame, pair_rects)
    else:
        center = closest_to_point(frame, pair_rects, last_pos)
    last_pos = center

    to_send = '{}:{}\n'.format(
        round(time.time(), 3), round(degrees(horizontal_angle(center[0])), 3))
    print(to_send)
    # s.send(bytearray(to_send, 'utf-8'))

    cv2.imshow('frame', frame)


if __name__ == "__main__":
    # connect_tcp()
    # send_times()

    fps = FPS().start()

    while (True):
        try:
            find_tape()
            fps.update()
            fps.stop()
            print(fps.fps())
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except ConnectionResetError or BrokenPipeError:
            pass
            # s.detach()
            # connect_tcp()

    CAP.release()
    cv2.destroyAllWindows()
