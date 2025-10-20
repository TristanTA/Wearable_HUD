from gps.gps_class import GPS_Data
from compass.compass_class import Compass_Data

def test_data():
    gps = GPS_Data(
        latitude=43.4931,
        longitude=-112.0401,
        altitude=1440.5,
        accuracy=3.2,
        speed=1.6
        )
    compass = Compass_Data(
        heading = 0,
        pitch = 0,
        roll = 0
    )
    
    return gps, compass