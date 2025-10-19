from camera.current_feed import start_live_feed
from gps.gps_class import GPS_Data

def main():
    gps = GPS_Data(
    latitude=43.4931,
    longitude=-112.0401,
    altitude=1440.5,
    accuracy=3.2,
    speed=1.6
    )

    print("GPS:", gps.Get())

    start_live_feed()

if __name__ == "__main__":
    main()