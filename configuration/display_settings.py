from configuration.settings.fps_settings import display_fps

def apply_settings(frame, fps: float, show_fps: bool = True):
    DISPLAY_FPS = show_fps
    display_fps(frame, fps)