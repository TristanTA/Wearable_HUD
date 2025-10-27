from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from emg_band.data_tracker import InputTracker

from kivy.lang import Builder
Builder.load_file("main.kv")

class EMGLayout(BoxLayout):
    pass

class EMGApp(App):
    def build(self):
        return EMGLayout()
    
    def run_tracker(self):
        if not hasattr(self, "tracker"):
            self.tracker = InputTracker(log_interval=0.1)  # 10 Hz logging rate
        self.tracker.start()
        self.ui_event = Clock.schedule_interval(self.display_tracker, 0.1)

    def stop_tracker(self):
        if hasattr(self, "tracker"):
            self.tracker.stop()
        if hasattr(self, "ui_event"):
            Clock.unschedule(self.display_tracker)


    def display_tracker(self, dt):
        data  = self.tracker.get_package()
        _, mouseX, mouseY, mouseVel, scrollVel, mouse1, mouse2, mouse3, keys = data
        self.root.ids.mouse_coord.text = f"Mouse Position: ({mouseX}, {mouseY})"
        self.root.ids.mouse_button1_status.text = f"Button 1: {mouse1}"
        self.root.ids.mouse_button2_status.text = f"Button 2: {mouse2}"
        self.root.ids.mouse_button3_status.text = f"Button 3: {mouse3}"
        self.root.ids.mouse_velocity.text = f"Mouse Velocity: {mouseVel}"
        self.root.ids.scroll_velocity.text = f"Scroll Velocity: {scrollVel}"
        self.root.ids.pressed_keys.text = f"Pressed Keys: {keys}"