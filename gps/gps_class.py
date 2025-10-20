class GPS_Data:
    def __init__(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None):
        self._latitude: float = latitude
        self._longitude: float = longitude
        self._altitude: float = altitude
        self._accuracy: float = accuracy
        self._speed: float = speed

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
        return package