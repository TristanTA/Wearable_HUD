import cv2
import time

from configuration.display_settings import apply_settings

def start_live_feed():
    start_time = time.time()
    frame_count = 0
    fps = None

    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        if fps != None:
            apply_settings(frame, fps, show_fps=True)

        cv2.imshow("Live Feed", frame)
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()