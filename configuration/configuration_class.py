from typing import Optional

from camera.camera_class import Camera
from configuration.settings.fps_settings import display_fps
from gps.gps_class import GPS
from compass.compass_class import Compass

class Configuration:
    def __init__(self, camera: Optional[Camera] = None, gps: Optional[GPS] = None, compass: Optional[Compass] = None, show_fps: Optional[bool] = None):
        self.camera: Camera = camera
        self.gps: GPS = gps
        self.compass: Compass = compass
        self.show_fps: bool = show_fps

    def display_configuration(self):
        if self.show_fps:
            display_fps(frame=self.camera.frame, fps=self.camera.fps)
        if self.gps:
            self.gps.display_gps(frame=self.camera.frame)
        if self.compass:
            self.compass.display_compass(frame=self.camera.frame)