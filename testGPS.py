import serial
from micropyGPS import MicropyGPS
import time

gps = MicropyGPS(1, 'dd')  

serial_port = serial.Serial('/dev/ttyAMA1', 4800, timeout=1)

def get_gps_data():
    while True:
        data = serial_port.readline().decode('ascii', errors='replace').strip()
        if data.startswith('$'):
            for char in data:
                gps.update(char)

        if gps.valid:
            print(f"Latitude: {gps.latitude[0]:.5f} {gps.latitude[1]}")
            print(f"Longitude: {gps.longitude[0]:.5f} {gps.longitude[1]}")
            print(f"Altitude: {gps.altitude} meters")
            print(f"Speed: {gps.speed[2]} km/h")
            print(f"Date: {gps.date_string('long')}")
            print(f"Time: {gps.time_string()}")
            print()
        time.sleep(1)

if __name__ == "__main__":
    try:
        get_gps_data()
    except KeyboardInterrupt:
        print("程序已终止")
