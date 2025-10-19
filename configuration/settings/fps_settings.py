import cv2

def display_fps(frame, fps: float):
    fps_text = f"FPS: {fps:.1f}"
    cv2.putText(frame, fps_text, (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
