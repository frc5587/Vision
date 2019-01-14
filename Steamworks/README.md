# PiVision
---
This project is designed to run Team 5587's vision processing on a Raspberry Pi 3.  
Please note that it is still a work in progress, and all code is *undocumented*.

Our Raspberry Pi runs Raspbian Jessie Lite. In order to get the same results we did, we reccomend that you follow the steps we did, in the order we did them.
## Installation

1. Install Raspbian Jessie Lite from [here](https://www.raspberrypi.org/downloads/raspbian/)  
2. Enable SSH by running `sudo raspi-config`
3. Follow [this tutorial](http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/) on how to install openCV with python support. __It will take a few hours.__ While he strongly reccomends the use of virtual environments, they aren't necessary in this use case. The Pi shouldn't ever need to run anything besides the vision code we give it. We also reccomend using python3.
4. Install pynetworktables by running `sudo pip3 install pynetworktables` - At this point our codebase should be able to run.
5. Install v4l2-ctl, a part of the v4l2-utils package by running `sudo apt-get install v4l2-utils`. You will need this for controlling your camera settings.

## Resources
* You can find how our script calculates FOV [here](http://vrguy.blogspot.com/2013/04/converting-diagonal-field-of-view-and.html).
* Learn more about doing vision properly [from Team 254.](https://www.team254.com/documents/vision-control/)
* Make yourself familiar with GRIP. [ScreenStepsLive](https://wpilib.screenstepslive.com/s/4485/m/24194/l/463566-introduction-to-grip) has some pretty good documentation.
