import cv2

from camera.camera_class import Camera
from compass.compass_class import Compass
from configuration.configuration_class import Configuration
from gps.gps_class import GPS

def main():
    cam = Camera()
    compass = Compass(0)
    gps = GPS(43.8260, -111.7897, heading=compass.get_heading())
    con = Configuration(camera=cam, gps=gps, compass=compass, show_fps = True)
    while cam.update():
        frame, fps = cam.get()

        con.display_configuration()

        counter = 1
        compass.set(heading = counter)
        counter += 10

        cv2.imshow("HUD", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    frame, fps = cam.get()
    cv2.imshow("HUD", frame)

if __name__ == "__main__":
    main()