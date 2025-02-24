import os
import time
import requests
from PIL import Image
import serial

def get_gps_coordinates():
    # lire data
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA'):
            lat, lon = parse_gpgga(line)  
            if lat and lon:
                return lat, lon
        time.sleep(0.5)

def parse_gpgga(data):
    """GPGGA"""
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[2])  # LAT
        lat_dir = parts[3]  # N/S
        lon = convert_to_degrees(parts[4])  # LON
        lon_dir = parts[5]  # E/W
        
        if lat and lon:
            lat = -lat if lat_dir == 'S' else lat
            lon = -lon if lon_dir == 'W' else lon
            return lat, lon
    return None, None

def convert_to_degrees(raw_value):
    """ NMEA en decimal"""
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

def get_google_map(lat, lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=15&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

if __name__ == "__main__":
    API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"  # API GOOGLE MAP
    
    try:
        print("-------GPS---------")
        latitude, longitude = get_gps_coordinates()
        print(f"Coordonnées obtenues avec succès ! LAT: {latitude}, LON: {longitude}")
        
        map_file = get_google_map(latitude, longitude, API_KEY)
        
        # show image
        img = Image.open(map_file)
        
    except Exception as e:
        print(f"error: {str(e)}")
