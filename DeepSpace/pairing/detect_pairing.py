import cv2
import numpy as np
from math import atan, sqrt

FOCAL_LENGTH = 333.82
FRAME_CENTER = (int(640 / 2), int(480 / 2))

ANGLE_TOLERANCE_DEG = 2

# Green
color_lower = np.array([50, 180, 50])
color_upper = np.array([120, 255, 255])

# Blue
# color_lower = np.array([100, 180, 50])
# color_upper = np.array([140, 255, 255])


def get_pair_rects(contours):
    """Get all valid pairs of tape in rect form given a list of OpenCV contours.

    Using the angles and center coordinates associated with each of the
    contours, possible pairs of tape are identified. However, there is no
    verification done to ensure that contours are valid pieces of tape, as the
    function assumes that they are valid.

    If no valid pairs are detected in the given list of contours, an empty
    list is returned in place of a list that ressembles
    [(rect1, rect2), (rect3, rect4), ... ]

    Arguments:
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

        # if rect[1][0] <= 25.0 or rect[1][1] <= 25.0:
        #     continue

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

    return rect_pairs


def get_pairs(rects):
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


def find_pair_centers(rect_pairs):
    """Find all of the pair centers given a list of pairs of rotated rectangles.

    The function iterates through a list of pairs of rotated rectangles,
    storing the center of each pair in a list to be returned by the function,
    in which the indexes between a pair and its center match up. If the
    rect_pairs list is empty, an empty list of centers is returned.

    Arguments:
        rect_pairs {list} -- list of pairs of rotated rectangles

    Returns:
        list -- centers found from the list of rotated rect pairs
    """

    centers = []
    for rect1, rect2 in rect_pairs:
        center = midpoint(rect1[0], rect2[0])
        centers.append(center)

    return centers


def closest_center(rect_pairs):
    """Gets the center of the rectangle pair closest to the center of the frame.

    Iterates through the rotated rectangle pairs, finding the rect pair that
    is closest to the center of the frame and then returning the center point
    of that rect pair or None if the rect_pairs list is empty. This function,
    however, does not detect center point of a frame, but uses the global
    FRAME_CENTER variable in this script.

    Arguments:
        rect_pairs {list} -- list of pairs of rotated rectangles

    Returns:
        tuple[int, int] or None -- the coordinates of the center of the rect
                                   pair closest to the center of the frame
    """
    centers = find_pair_centers(rect_pairs)

    min_dist = min_center = None
    for center in centers:
        dist = distance(center, FRAME_CENTER)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_center = center

    return min_center


def closest_pair(rect_pairs):
    centers = find_pair_centers(rect_pairs)

    min_dist = min_index = None
    for index, center in enumerate(centers):
        dist = distance(center, FRAME_CENTER)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_index = index

    return rect_pairs[min_index]


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


def midpoint(point1, point2):
    """Find the midpoint between point1 and point2.

    Arguments:
        point1 {tuple[int, int]} -- the first point
        point2 {tuple[int, int]} -- the second point

    Returns:
        tuple[int, int] -- the coordinates of the midpoint
    """

    x, y = (int((point1[0] + point2[0]) / 2), int((point1[1] + point2[1]) / 2))
    return (x, y)


def get_tape_frame(tape_pair):
    boxes = np.array([cv2.boxPoints(tape) for tape in tape_pair])

    all_x = boxes[:, :, 0].flatten()
    all_y = boxes[:, :, 1].flatten()

    top_left = (np.min(all_x), np.min(all_y))
    bottom_right = (np.max(all_x), np.max(all_y))
    return (top_left[0], top_left[1], bottom_right[0], bottom_right[1])


def find_tape_rect(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)

    # Find all valid pair rects, and reutrn if none found
    # pair_rects = get_pair_rects(contours)
    rects = get_rects_by_height(contours)
    pair_rects = get_pairs(rects)
    if len(pair_rects) == 0 or pair_rects is None:
        return None

    # If found, continue on and post results
    pair = closest_pair(pair_rects)
    return get_tape_frame(pair)
