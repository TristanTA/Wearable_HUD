from camera.current_feed import start_live_feed
from data.gps import GPS_Data

def main():
    gps = GPS_Data()
    print("GPS:", gps.Get())

    start_live_feed()

if __name__ == "__main__":
    main()