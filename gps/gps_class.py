class GPS:
    def __init__(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.altitude: float = altitude
        self.accuracy: float = accuracy
        self.speed: float = speed

    def set(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None):
        self.latitude = float(f"{latitude}.:5f")
        self.longitude = float(f"{longitude}.:5f")
        self.altitude = float(f"{altitude}.:5f")
        self.accuracy = float(f"{accuracy}.:5f")
        self.speed = float(f"{speed}.:5f")

    def get(self):
        package = {
            "Latitude": self.latitude,
            "Longitude": self.longitude,
            "Altitude": self.altitude,
            "Accuracy": self.accuracy,
            "Speed": self.speed
            }
        return package
    
    def display_gps(self, frame):
        pass