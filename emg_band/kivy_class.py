from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder
Builder.load_file("main.kv")

class EMGLayout(BoxLayout):
    pass

class EMGApp(App):
    def build(self):
        return EMGLayout()

if __name__ == "__main__":
    EMGApp().run()