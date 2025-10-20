from camera.current_feed import start_live_feed
from init_test_data import test_data

def main():
    gps, compass = test_data()
    start_live_feed(gps, compass)

if __name__ == "__main__":
    main()