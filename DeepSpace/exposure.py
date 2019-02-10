import cv2

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, -7.0)

while(True):
    _, frame = cap.read()
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()