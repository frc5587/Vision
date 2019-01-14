#!/usr/bin/python3

"""
Simple skeleton program for running an OpenCV pipeline generated by GRIP and using NetworkTables to send data.

Users need to:

1. Import the generated GRIP pipeline, which should be generated in the same directory as this file.
2. Set the network table server IP. This is usually the robots address (roborio-TEAM-frc.local) or localhost
3. Configure camera setup settings.
4. Handle putting the generated code into NetworkTables
"""

import cv2
from networktables import NetworkTable
from grip import GripPipeline  # TODO set module (filename) and class, if needed.
# Ex. from pipleline (for pipeline.py) import VisionTask (for class VisionTask)
from conversion import Angles
from subprocess import call

def extra_processing(pipeline: GripPipeline):
    """
    Performs extra processing on the pipeline's outputs and publishes data to NetworkTables.
    :param pipeline: the pipeline that just processed an image
    :return: None
    """
    # TODO: Users need to implement this.
    # Useful for converting OpenCV objects (e.g. contours) to something NetworkTables can understand.

    converter = Angles()

    (imgx,imgy) = pipeline.get_mat_info_size

    contours = pipeline.filter_contours_output

    center_x_positions = []
    center_y_positions = []
    widths = []
    heights = []

    x_angles = []
    y_angles = []
    dist = 0.0

    #sorts contours
    if(len(pipeline.filter_contours_output) > 1):
        boundingBoxes = [cv2.boundingRect(c) for c in pipeline.filter_contours_output]
        (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
            key=lambda b:b[1][1], reverse=False))
        dummy, distY, dummy2, distH = cv2.boundingRect(contours[0])
        dist = converter.dist(distY + distH / 2)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        center_x_positions.append(x + w / 2)  # X and Y are coordinates of the top-left corner of the bounding box
        center_y_positions.append(y + h / 2)
        widths.append(w)
        heights.append(y)
        x_angles.append(converter.x_angle(x + w / 2))
        y_angles.append(converter.y_angle(y + h / 2))

    extra = NetworkTable.getTable('/GRIP/preprocessed')
    extra.putNumberArray('x', center_x_positions)
    extra.putNumberArray('y', center_y_positions)
    extra.putNumberArray('width', widths)
    extra.putNumberArray('height', heights)

    usable = NetworkTable.getTable('/GRIP/postprocessed')
    usable.putNumberArray('x angles', x_angles)
    usable.putNumberArray('y angles', y_angles)
    usable.putNumber('distance', dist)


def main():
    NetworkTable.setTeam(5587)  # TODO set your team number
    NetworkTable.setClientMode()
    NetworkTable.setIPAddress('10.55.87.2') # TODO switch to RIO IP, or IP of laptop running OutlineViewer for setup
    NetworkTable.initialize()

    #TODO find what v4l2-ctl settings you need. Pass each commandline option through this array. REQUIRES v4l2-utils to be installed.
    call(["v4l2-ctl","--set-ctrl=exposure_auto=1","--set-ctrl=exposure_absolute=9","--set-ctrl=white_balance_temperature_auto=0"],shell=False)

    cap = cv2.VideoCapture(0)
    pipeline = GripPipeline()
    while True:
        ret, frame = cap.read()
        if ret:
            pipeline.process(frame)  # TODO add extra parameters if the pipeline takes more than just a single image
            extra_processing(pipeline)


if __name__ == '__main__':
    main()