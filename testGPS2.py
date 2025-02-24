import os
import time
import requests
import pygame
import serial

def get_gps_coordinates():
    """GPS """
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA'):
            lat, lon = parse_gpgga(line)  
            if lat and lon:
                return lat, lon
        time.sleep(0.5)

def parse_gpgga(data):
    """GPGGA NMEA """
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[2])  
        lat_dir = parts[3]  # N/S
        lon = convert_to_degrees(parts[4])  
        lon_dir = parts[5]  # E/W
        
        if lat and lon:
            lat = -lat if lat_dir == 'S' else lat
            lon = -lon if lon_dir == 'W' else lon
            return lat, lon
    return None, None

def convert_to_degrees(raw_value):
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

def get_google_map(lat, lon, api_key):
    """ Google Maps """
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=15&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

def display_map():
    """GPS"""
    pygame.init()
    
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("GPS")
    
    running = True
    while running:
        try:
            latitude, longitude = get_gps_coordinates()
            print(f"Coordonnées obtenues avec succès !LAT: {latitude}, LON: {longitude}")

            map_file = get_google_map(latitude, longitude, API_KEY)
            print("map change")


            map_image = pygame.image.load(map_file)
            screen.blit(map_image, (0, 0)) 
            pygame.display.flip()  


            time.sleep(3)

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

        except Exception as e:
            print(f" error : {str(e)}")
            running = False

    pygame.quit()

if __name__ == "__main__":
    API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"  # 你的 Google Maps API Key
    display_map()
