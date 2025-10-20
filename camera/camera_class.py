import cv2, time

class Camera:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.lens_frame = None
        self.hud_frame = None

    def update(self):
        ret, self.lens_frame = self.cap.read()
        if not ret:
            return False
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        self.fps = self.frame_count / elapsed if elapsed > 0 else 0
        return True

    def get(self):
        return self.hud_frame, self.fps

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()