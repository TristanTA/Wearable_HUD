import requests, numpy as np, cv2, os
from dotenv import load_dotenv

from configuration.settings.colors import LIMA
from compass.compass_class import Compass

class GPS:
    def __init__(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None, heading: int = None):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.altitude: float = altitude
        self.accuracy: float = accuracy
        self.speed: float = speed
        self._cached_tile = None
        self._cached_coords = (None, None)
        self.heading = heading

    def set(self, latitude: float = None, longitude: float = None, altitude: float = None, accuracy: float = None, speed: float = None):
        self.latitude = round(latitude, 5)
        self.longitude = round(longitude, 5)
        self.altitude = round(altitude, 5)
        self.accuracy = round(accuracy, 5)
        self.speed = round(speed, 5)

    def get(self):
        package = {
            "Latitude": self.latitude,
            "Longitude": self.longitude,
            "Altitude": self.altitude,
            "Accuracy": self.accuracy,
            "Speed": self.speed
            }
        return package

    def get_map_tile(self, lat, lon, zoom=17, size=(150,150)):
        if (self._cached_coords[0] is not None
            and self._cached_coords[1] is not None
            and abs(lat - self._cached_coords[0]) < 0.0005
            and abs(lon - self._cached_coords[1]) < 0.0005):
            return self._cached_tile
        else:
            load_dotenv()
            key= os .getenv("GOOGLE_STATIC_MAP_API_KEY")
            url = (
                f"https://maps.googleapis.com/maps/api/staticmap?"
                f"center={lat},{lon}&zoom={zoom}"
                f"&size={size[0]}x{size[1]}&maptype=roadmap&key={key}"
            )
            resp = requests.get(url)
            if resp.status_code != 200:
                return np.zeros((size[1], size[0], 3), np.uint8)
            arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
            self._cached_tile = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            self._cached_coords = (lat, lon)
            return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        
    def draw_player_arrow(self, frame, heading_deg, map_pos, map_size):
        cx, cy = map_pos[0] + map_size // 2, map_pos[1] + map_size // 2
        # Triangle pointing upward (local coordinates)
        pts = np.array([[0, -8], [-5, 6], [5, 6]], np.int32)
        # Rotate by heading
        theta = np.deg2rad(-heading_deg)
        rot = np.array([[np.cos(theta), -np.sin(theta)],
                        [np.sin(theta),  np.cos(theta)]])
        pts = (pts @ rot.T + [cx, cy]).astype(int)
        cv2.fillConvexPoly(frame, pts, LIMA)



    def display_gps(self, frame):
        height, width, _ = frame.shape
        map_size = 100
        margin = 10
        x1 = width - map_size - margin
        y1 = height - map_size - margin
        map_pos = (x1, y1)
        map_center = (x1 + map_size // 2, y1 + map_size // 2)
        map_tile = self.get_map_tile(self.latitude, self.longitude, size=(map_size, map_size))
        frame[y1:y1+map_size, x1:x1+map_size] = map_tile
        if self.heading is not None:
            self.draw_player_arrow(frame, self.heading, map_pos, map_size)
        else:
            cv2.circle(frame, map_center, 4, LIMA, -1)