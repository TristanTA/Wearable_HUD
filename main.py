import cv2

from camera.camera_class import Camera
from compass.compass_class import Compass
from configuration.configuration_class import Configuration

def main():
    cam = Camera()
    compass = Compass(0)
    con = Configuration(camera=cam, compass=compass, show_fps = True)
    while cam.update():
        frame, fps = cam.get()

        con.display_configuration()

        cv2.imshow("HUD", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    frame, fps = cam.get()
    cv2.imshow("HUD", frame)

if __name__ == "__main__":
    main()