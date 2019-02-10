import cv2
import numpy as np

cap = cv2.VideoCapture(1)

# color_lower = np.array([35, 0, 216])
# color_upper = np.array([47, 2, 255])
color_lower = np.array([94, 78, 46])
color_upper = np.array([129, 187, 255])
distance = 1
focal_length = 333.82

def calc_width_in(px):
    #p = apparent width in pixels
    width_inches = (px * distance)/focal_length
    print("Width in Pixels: " + str(px) + "Apparent Length (in)" + str(width_inches))

while(True):
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color_lower, color_upper)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contours), contours) for contours in contours]

    if(len(contour_sizes) > 0):
        maxElement = max(contour_sizes, key=lambda x: x[0])
        rect = cv2.minAreaRect(maxElement[1])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
        w = rect[0][0]
        calc_width_in(w)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
