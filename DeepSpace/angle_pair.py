import cv2
import imutils
import numpy as np
from random import randint
from timerfunc import timerfunc
import os

imgs_path = "./DeepSpace/sample-images/"
onlyfiles = [
    f for f in os.listdir(imgs_path)
    if os.path.isfile(os.path.join(imgs_path, f)) and
    os.path.splitext(f)[1] == ".png"
]
print(onlyfiles)

color_lower = np.array([0, 0, 0])
color_upper = np.array([255, 10, 255])
percent_reduce = 0.7
ANGLE_TOLERANCE_DEG = 2


@timerfunc
def get_pairs(contours):
    """Get all valid pairs of tape given a list of OpenCV contours

    Arguments:
        contours {list} -- list/numpy array of all of the contours
                            in a given frame

    Returns:
        list -- list of tuples, where each tuple is a pair of contours
    """

    rect_pairs = []
    for index, cnt in enumerate(contours):
        # Rotated rect - ( center (x,y), (width, height), angle of rotation )
        rect = cv2.minAreaRect(cnt)
        center_x, center_y = rect[0]
        rect_angle = -round(rect[2], 2)

        cv2.putText(img, str(rect_angle), (int(center_x), int(center_y)),
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

    return rect_pairs


for file in onlyfiles:
    img = cv2.imread(imgs_path + file)
    height, width = img.shape[:2]
    img = imutils.resize(img, int(width * percent_reduce),
                         int(height * percent_reduce))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)

    rect_pairs = get_pairs(contours)

    for rects in rect_pairs:
        color = (randint(128, 255), randint(128, 255), randint(128, 255))

        for rect in rects:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.line(img, tuple(box[0]), tuple(box[-1]), (0, 255, 0), 3)
            cv2.drawContours(img, [box], 0, tuple(color), 2)

    cv2.imshow('frame', img)
    cv2.waitKey(0)

cv2.destroyAllWindows()
