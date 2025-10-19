class GPS_Data:
    def __init__(self):
        self._latitude: float
        self._longitude: float
        self._altitude: float
        self._accuracy: float
        self._speed: float

    def Set(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None):
        self._latitude = float(f"{latitude}.:5f")
        self._longitude = float(f"{longitude}.:5f")
        self._altitude = float(f"{altitude}.:5f")
        self._accuracy = float(f"{accuracy}.:5f")
        self._speed = float(f"{speed}.:5f")

    def Get(self):
        package = {
            "Latitude": self._latitude,
            "Longitude": self._longitude,
            "Altitude": self._altitude,
            "Accuracy": self._accuracy,
            "Speed": self._speed
            }