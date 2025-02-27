import threading
import json
import os
import time
import requests
import pygame
import serial
import paho.mqtt.client as mqtt

broker = "192.168.1.205"
port = 1883
zoom_topic = "GPS/zoom"
destination_topic = "GPS/destination"
zoom_level = 15
destination_address = None
destination_coords = None
API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"

def input_address():
    """ entre address """
    global destination_address, destination_coords
    while True:
        new_address = input("destination: ")
        if new_address:
            destination_address = new_address
            destination_coords = get_destination_coordinates(new_address)
            client.publish(destination_topic, new_address)
            print(f"sent: {new_address} -> {destination_coords}")


def on_message(client, userdata, msg):
    global zoom_level, destination_address, destination_coords
    try:
        message = msg.payload.decode("utf-8")
        if msg.topic == zoom_topic:
            if message == "zoom":
                zoom_level = min(zoom_level + 1, 20)
            elif message == "dezoom":
                zoom_level = max(zoom_level - 1, 5)
            print(f"Zoom level set to {zoom_level}")
        elif msg.topic == destination_topic:
            destination_address = message
            destination_coords = get_destination_coordinates(destination_address)
            print(f"Received new destination: {destination_address} -> {destination_coords}")
    except Exception as e:
        print(f"MQTT error: {e}")

client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port, 60)
client.subscribe(zoom_topic)
client.subscribe(destination_topic)
client.loop_start()

def publish_gps(lat, lon):
    payload = json.dumps({"latitude": lat, "longitude": lon})
    client.publish("gps/position", payload)

def get_gps_coordinates():
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA'):
            lat, lon = parse_gpgga(line)
            if lat and lon:
                return lat, lon
        time.sleep(0.5)

def parse_gpgga(data):
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[2])
        lat_dir = parts[3]
        lon = convert_to_degrees(parts[4])
        lon_dir = parts[5]
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

def get_destination_coordinates(address):
    """  Google Geocoding API  """
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None

def get_route(start_lat, start_lon, dest_lat, dest_lon):
    """ Google Directions API  """
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lon}&destination={dest_lat},{dest_lon}&mode=driving&key={API_KEY}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        return response["routes"][0]["overview_polyline"]["points"]
    return None

def get_google_map(lat, lon, route=None):
    """map obtenir"""
    global zoom_level, destination_coords
    base_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom_level}&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={API_KEY}"
    
    if destination_coords:
        base_url += f"&markers=color:blue%7C{destination_coords[0]},{destination_coords[1]}"
    
    if route:
        base_url += f"&path=color:0x0000ff|weight:5|enc:{route}"

    response = requests.get(base_url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

def display_map():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))  # 扩展窗口以显示文本信息
    pygame.display.set_caption("GPS Navigation")

    font = pygame.font.Font(None, 24)  # 设定字体大小
    running = True

    while running:
        try:
            latitude, longitude = get_gps_coordinates()
            print(f"GPS Location: LAT: {latitude}, LON: {longitude}")
            publish_gps(latitude, longitude)

            route = None
            if destination_coords:
                route = get_route(latitude, longitude, *destination_coords)

            map_file = get_google_map(latitude, longitude, route)
            print("Updated map with navigation route")

            map_image = pygame.image.load(map_file)
            screen.fill((255, 255, 255))  
            screen.blit(map_image, (0, 0)) 

            pygame.draw.rect(screen, (200, 200, 200), (600, 0, 200, 400))  

            destination_text = f"Destination:\n{destination_address if destination_address else 'None'}"
            current_coords_text = f"Current:\nLAT: {latitude:.6f}\nLON: {longitude:.6f}"
            target_coords_text = "Target:\n"
            if destination_coords:
                target_coords_text += f"LAT: {destination_coords[0]:.6f}\nLON: {destination_coords[1]:.6f}"
            else:
                target_coords_text += "N/A"

            text_surfaces = [
                font.render(destination_text, True, (0, 0, 0)),
                font.render(current_coords_text, True, (0, 0, 0)),
                font.render(target_coords_text, True, (0, 0, 0)),
            ]

            y_offset = 20
            for text_surface in text_surfaces:
                screen.blit(text_surface, (610, y_offset))
                y_offset += 80  

            pygame.display.flip()
            time.sleep(3)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

        except Exception as e:
            print(f"Error: {str(e)}")
            running = False

    pygame.quit()


if __name__ == "__main__":
    input_thread = threading.Thread(target=input_address, daemon=True)
    input_thread.start()
    display_map()
