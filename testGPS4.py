import os
import time
import requests
import pygame
import serial
import paho.mqtt.client as mqtt
import math  # 用于计算箭头方向

# MQTT 配置
broker = "192.168.1.205"
port = 1883
topic = "GPS/zoom"
zoom_level = 15   

# 解析 GPGGA 语句（获取纬度、经度）
def parse_gpgga(data):
    """解析 GPGGA NMEA 语句，返回纬度和经度"""
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

# 解析 GPVTG 语句（获取速度 & 方向）
def parse_gpvtg(data):
    """解析 GPVTG NMEA 语句，返回速度（km/h）和方向（度）"""
    parts = data.split(',')
    if len(parts) > 7:
        try:
            speed_kmh = float(parts[7])  # 获取速度（单位：km/h）
            direction = float(parts[1])  # 获取方向（单位：度）
            return speed_kmh, direction
        except ValueError:
            return None, None
    return None, None

# GPS 数据转换（NMEA 格式 → 十进制度）
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

# 获取 GPS 数据（包括 位置、速度、方向）
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
            zoom_level = min(zoom_level + 1, 20)  # 放大
        elif message == "dezoom":
            zoom_level = max(zoom_level - 1, 5)   # 缩小
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
    angle_rad = math.radians(direction)  # 角度转弧度
    end_x = center_x + arrow_length * math.sin(angle_rad)  # X 坐标（正北为 0°）
    end_y = center_y - arrow_length * math.cos(angle_rad)  # Y 坐标（负号保证方向正确）

    # 绘制箭头
    pygame.draw.line(screen, (255, 0, 0), (center_x, center_y), (end_x, end_y), 4)  # 画主线
    pygame.draw.circle(screen, (255, 0, 0), (int(end_x), int(end_y)), 5)  # 画箭头端点

# 显示地图
def display_map():
    """在 Pygame 窗口中显示 GPS 位置、速度和方向"""
    pygame.init()
    
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("GPS 追踪")
    font = pygame.font.Font(None, 24)

    running = True
    while running:
        try:
            # 获取 GPS 数据
            latitude, longitude, speed, direction = get_gps_data()
            print(f"GPS: LAT: {latitude}, LON: {longitude}, 速度: {speed} km/h, 方向: {direction}°")

            # 获取地图
            map_file = get_google_map(latitude, longitude, API_KEY)
            map_image = pygame.image.load(map_file)

            # 刷新窗口
            screen.blit(map_image, (0, 0)) 

            # 显示速度 & 方向
            speed_text = font.render(f"速度: {speed:.2f} km/h", True, (255, 255, 255))
            direction_text = font.render(f"方向: {direction:.2f}°", True, (255, 255, 255))

            screen.blit(speed_text, (10, 10))  
            screen.blit(direction_text, (10, 40))  

            # **调用绘制箭头的函数**
            draw_arrow(screen, direction)

            pygame.display.flip()
            time.sleep(3)
            
            # 事件监听
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
        
        except Exception as e:
            print(f"error: {str(e)}")
            running = False

    pygame.quit()

# 主程序
if __name__ == "__main__":
    API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"
    display_map()
