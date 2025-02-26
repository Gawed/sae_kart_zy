import os
import time
import requests
import pygame
import serial
import math
import paho.mqtt.client as mqtt

# MQTT 配置
broker = "192.168.1.205"
port = 1883
topic = "GPS/zoom"
zoom_level = 15

# GPS 数据转换（NMEA → 十进制度）
def convert_to_degrees(raw_value):
    """转换 NMEA 坐标格式为十进制度"""
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

# 解析 GPGGA 语句（获取纬度 & 经度）
def parse_gpgga(data):
    """解析 GPGGA NMEA 语句，返回纬度和经度"""
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

# 解析 GPVTG 语句（获取速度 & 方向）
def parse_gpvtg(data):
    """解析 GPVTG NMEA 语句，返回速度（km/h）和方向（°）"""
    parts = data.split(',')
    if len(parts) > 7:
        try:
            speed_kmh = float(parts[7])
            direction = float(parts[1])
            return speed_kmh, direction
        except ValueError:
            return None, None
    return None, None

# 获取 GPS 数据
def get_gps_data():
    """获取 GPS 位置、速度和方向"""
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

# 获取 Google 静态地图
def get_google_map(lat, lon, api_key):
    """从 Google Maps API 获取静态地图"""
    global zoom_level
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom={zoom_level}&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

# 处理 MQTT 消息
def on_message(client, userdata, msg):
    """MQTT 处理消息（缩放地图）"""
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

# 初始化 MQTT 连接
client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port, 60)
client.subscribe(topic)
client.loop_start()

# 在地图上绘制方向箭头
def draw_arrow(screen, direction):
    """在屏幕中央绘制指示方向的箭头"""
    if direction is None:
        return  

    center_x, center_y = 300, 200  # 箭头基准位置
    arrow_length = 30  # 箭头长度

    # 计算箭头端点坐标
