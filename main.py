import cv2
import numpy as np

from camera.camera_class import Camera
from compass.compass_class import Compass
from configuration.configuration_class import Configuration
from gps.gps_class import GPS

def main():
    cam = Camera()
    cam.update()  # grab first frame
    camera_frame = cam.lens_frame
    hud_layer = np.zeros_like(camera_frame)
    cam.hud_frame = hud_layer
    compass = Compass(0)
    gps = GPS(43.8260, -111.7897, heading=compass.get_heading())
    con = Configuration(camera=cam, gps=gps, compass=compass, show_fps = True)
    while cam.update():
        camera_frame = cam.lens_frame
        hud_layer = cam.hud_frame

        con.display_configuration()

        counter = 1
        compass.set(heading = counter)
        counter += 10

        combined = cv2.addWeighted(camera_frame, 1.0, hud_layer, 1.0, 0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.imshow("HUD", combined)

if __name__ == "__main__":
    main()