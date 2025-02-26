
import json
import os
import time
import requests
import pygame
import serial
import paho.mqtt.client as mqtt
import math  

# MQTT 
broker = "192.168.1.205"
port = 1883
topic = "GPS/zoom"
zoom_level = 15   

# GPGGA 
def parse_gpgga(data):
    """ GPGGA NMEA """
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

#  GPVTG
def parse_gpvtg(data):
    """GPVTG NMEA"""
    parts = data.split(',')
    if len(parts) > 7:
        try:
            speed_kmh = float(parts[7])  
            direction = float(parts[1]) 
            return speed_kmh, direction
        except ValueError:
            return None, None
    return None, None

# GPS （NMEA）
def convert_to_degrees(raw_value):
    """NMEA"""
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

# GPS 
def get_gps_data():
    """GPS"""
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    lat, lon, speed, direction = None, None, None, None
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')

        if line.startswith('$GPGGA'):
            lat, lon = parse_gpgga(line)  
        elif line.startswith('$GPVTG'):
            speed, direction = parse_gpvtg(line)

        if lat and lon and direction is not None:
            return lat, lon, speed, direction

        time.sleep(0.5)

# Google
def get_google_map(lat, lon, api_key):
    """从 Google Maps API"""
    global zoom_level
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom_level}&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

# MQTT
def on_message(client, userdata, msg):
    """MQTT"""
    global zoom_level
    try:
        message = msg.payload.decode("utf-8")
        if message == "zoom":
            zoom_level = min(zoom_level + 1, 20) 
        elif message == "dezoom":
            zoom_level = max(zoom_level - 1, 5) 
        print(f"Received MQTT message: {message}, zoom level set to {zoom_level}")
    except Exception as e:
        print(f"MQTT message processing error: {e}")

#  MQTT 
client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port, 60)
client.subscribe(topic)
client.loop_start()

import math
import pygame

def draw_arrow(screen, direction):
    if direction is None:
        return  
        
    center_x, center_y = 300, 200 
    arrow_length = 40
    arrow_width = 10 
 
    angle_rad = math.radians(direction)
    end_x = center_x + arrow_length * math.sin(angle_rad)
    end_y = center_y - arrow_length * math.cos(angle_rad)


    arrow_head_size = 10
    left_x = end_x + arrow_head_size * math.sin(angle_rad + math.radians(150))
    left_y = end_y - arrow_head_size * math.cos(angle_rad + math.radians(150))
    right_x = end_x + arrow_head_size * math.sin(angle_rad - math.radians(150))
    right_y = end_y - arrow_head_size * math.cos(angle_rad - math.radians(150))

    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (end_x, end_y), 4)

    pygame.draw.polygon(screen, (255, 0, 0), [(end_x, end_y), (left_x, left_y), (right_x, right_y)])


def display_map():
    """ Pygame """
    pygame.init()
    
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("GPS")
    font = pygame.font.Font(None, 24)

    running = True
    while running:
        try:
            
            latitude, longitude, speed, direction = get_gps_data()
            print(f"GPS: LAT: {latitude}, LON: {longitude}, 速度: {speed} km/h, 方向: {direction}°")
          
            map_file = get_google_map(latitude, longitude, API_KEY)
            map_image = pygame.image.load(map_file)

            screen.blit(map_image, (0, 0)) 

            speed_text = font.render(f"vitesse: {speed:.2f} km/h", True, (255, 255, 255))
            direction_text = font.render(f"direction: {direction:.2f}°", True, (255, 255, 255))

            screen.blit(speed_text, (10, 10))  
            screen.blit(direction_text, (10, 40))  

            draw_arrow(screen, direction)

            pygame.display.flip()
            time.sleep(3)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
        
        except Exception as e:
            print(f"error: {str(e)}")
            running = False

    pygame.quit()

if __name__ == "__main__":
    API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"
    display_map()
