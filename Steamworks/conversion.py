import math
from networktables import NetworkTables
class Angles:
    def __init__(self):
        self.diagonal_FOV = 68.5 #degrees
        self.horizontal_FOV = None
        self.vertical_FOV = None
        self.combined_aspect = None #800
        self.x_aspect = 640 #Image width
        self.y_aspect = 480 #Image height
        self.focal_length = None
        self.center_x = None
        self.center_y = None

        self.__find_FOVs()

        self.target_height = 2.0955 # in meters
        self.camera_height = 0.50 # in meters
        self.camera_y_angle_offset = .61 # in radians
    #Find FOV angles
    def __find_FOVs(self):
        self.center_x = self.x_aspect/2 -.5
        self.center_y = self.y_aspect/2 -.5
        self.combined_aspect = math.hypot(self.x_aspect,self.y_aspect)
        self.horizontal_FOV = 2*(math.atan( (math.tan(math.radians(self.diagonal_FOV))/2) * (self.x_aspect/self.combined_aspect) ))
        self.vertical_FOV = 2*(math.atan( (math.tan(math.radians(self.diagonal_FOV))/2) * (self.y_aspect/self.combined_aspect) ))
        self.focal_length = self.x_aspect / (2*math.tan(self.horizontal_FOV/2))


    def x_angle(self,u):
        u_deg = math.degrees(math.atan((u-self.center_x)/self.focal_length))
        u_deg = int(u_deg*1000)/1000.0
        return u_deg

    def y_angle(self,v):
        v_deg = -1*math.degrees(math.atan((v-self.center_y)/self.focal_length))
        v_deg = int(v_deg*1000)/1000.0
        return v_deg

    def dist(self,v):
        v_rad = math.atan((v-self.center_y)/self.focal_length)
        dist = (self.target_height-self.camera_height)/(math.tan(v_rad-self.camera_y_angle_offset+.0000000000001)) # extra added value prevents divide by zero
        dist = int(dist*1000)/1000.0
        return dist;
