# import the necessary packages
from detect_pairing import find_tape_rect
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import os

os.system(
    "uvcdynctrl -s 'Exposure, Auto' 1 && uvcdynctrl -s 'Exposure (Absolute)'" +
    " 0.1 && uvcdynctrl -s 'Brightness' 0.1")

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument(
    "-t",
    "--tracker",
    type=str,
    default="kcf",
    help="OpenCV object tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}
tracker_fn = OPENCV_OBJECT_TRACKERS[args["tracker"]]
tracker = None

# initialize the bounding box coordinates of the object we are going to track
initBB = None

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

# initialize the FPS throughput estimator
fps = None

# loop over frames from the video stream
while True:
    # grab the current frame
    frame = vs.read()

    # resize the frame (so we can process it faster) and grab the
    # frame dimensions
    # frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]

    # check to see if we are currently tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates of the object
        success, box = tracker.update(frame)

        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # update the FPS counter
        fps.update()
        fps.stop()

        # initialize the set of information we'll be displaying on
        # the frame
        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    else:
        print('Hello!')
        initBB = find_tape_rect(frame)
        if initBB is None:
            continue
        cv2.rectangle(frame, (initBB[0], initBB[1]), (initBB[0] + initBB[2], initBB[1] + initBB[3]), (0, 255, 255), 4)
        cv2.circle(frame, (int(W / 2), int(H / 2)), 5, (0, 255, 0), 5)

        tracker = tracker_fn()
        tracker.init(frame, initBB)
        fps = FPS().start()

        cv2.imshow("frameD", frame)

    # cv2.imshow('Frame', frame)
    # while True:
    #     print('Hello!')
    #     continue
    # # start OpenCV object tracker using the supplied bounding box
    # # coordinates, then start the FPS throughput estimator as well
    # tracker = tracker_fn()
    # tracker.init(frame, initBB)
    # fps = FPS().start()

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
