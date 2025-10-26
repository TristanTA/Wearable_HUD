from pynput import keyboard, mouse
import time
import math
import csv

class InputTracker:
    def __init__(self, log_interval: float = 0.1):
        self.mouse_location = (0.0, 0.0)
        self.mouse1 = False
        self.mouse2 = False
        self.mouse3 = False
        self.pressed_keys = set()

        self.prev_time = time.time()
        self.prev_pos = None
        self.scroll_velocity = 0.0
        self.mouse_velocity = 0.0
        self.last_log_time = 0.0

        self.file_name = "emg_data.csv"
        self.log_interval = log_interval  # seconds (e.g., 0.1 = 10 Hz)

        # Write CSV header
        with open(self.file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "mouse_x",
                "mouse_y",
                "mouse_velocity",
                "scroll_velocity",
                "mouse1",
                "mouse2",
                "mouse3",
                "pressed_keys"
            ])

    # --- Mouse events ---
    def on_move(self, x, y):
        current_time = time.time()
        if self.prev_pos:
            dt = current_time - self.prev_time
            if dt > 0:
                dx = x - self.prev_pos[0]
                dy = y - self.prev_pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                self.mouse_velocity = distance / dt
        self.prev_time = current_time
        self.prev_pos = (x, y)
        self.mouse_location = (x, y)
        self.maybe_store()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.mouse1 = pressed
        elif button == mouse.Button.right:
            self.mouse2 = pressed
        elif button == mouse.Button.middle:
            self.mouse3 = pressed
        self.mouse_location = (x, y)
        self.maybe_store()

    def on_scroll(self, x, y, dx, dy):
        current_time = time.time()
        if self.prev_time:
            dt = current_time - self.prev_time
            if dt > 0:
                self.scroll_velocity = abs(dy) / dt
        self.prev_time = current_time
        self.mouse_location = (x, y)
        self.maybe_store()

    # --- Keyboard events ---
    def on_press(self, key):
        try:
            self.pressed_keys.add(key.char)
        except AttributeError:
            self.pressed_keys.add(str(key))
        self.maybe_store()

    def on_release(self, key):
        try:
            self.pressed_keys.discard(key.char)
        except AttributeError:
            self.pressed_keys.discard(str(key))
        self.maybe_store()

    # --- Data retrieval and logging ---
    def get_package(self):
        return (
            round(time.time(), 4),
            round(self.mouse_location[0], 2),
            round(self.mouse_location[1], 2),
            round(self.mouse_velocity, 3),
            round(self.scroll_velocity, 3),
            self.mouse1,
            self.mouse2,
            self.mouse3,
            ",".join(self.pressed_keys)
        )

    def maybe_store(self):
        now = time.time()
        if now - self.last_log_time >= self.log_interval:
            self.store()
            self.last_log_time = now

    def store(self):
        with open(self.file_name, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self.get_package())

# --- Run trackers ---
tracker = InputTracker(log_interval=0.1)  # 10 Hz logging rate

with mouse.Listener(
    on_move=tracker.on_move,
    on_click=tracker.on_click,
    on_scroll=tracker.on_scroll
) as m_listener, keyboard.Listener(
    on_press=tracker.on_press,
    on_release=tracker.on_release
) as k_listener:
    m_listener.join()
    k_listener.join()