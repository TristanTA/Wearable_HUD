class Compass_Data:
    def __init__(self, heading: float = None, pitch: float = None, roll: float = None):
        self._heading: float = heading
        self._pitch: float = pitch
        self._roll: float = roll

    def Set(self, heading: float = None, pitch: float = None, roll: float = None):
        if heading:
            self._heading = heading
        if pitch:
            self._pitch = pitch
        if roll:
            self._roll = roll

    def Get(self):
        package = {"Heading": self._heading,
                   "Pitch": self._pitch,
                   "Roll": self._roll}
        return package