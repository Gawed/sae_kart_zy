import os
import time
import requests
import pygame
import serial

def get_gps_coordinates():
    """读取 GPS 数据"""
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA'):
            lat, lon = parse_gpgga(line)  
            if lat and lon:
                return lat, lon
        time.sleep(0.5)

def parse_gpgga(data):
    """解析 GPGGA NMEA 数据"""
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[2])  # 纬度
        lat_dir = parts[3]  # N/S
        lon = convert_to_degrees(parts[4])  # 经度
        lon_dir = parts[5]  # E/W
        
        if lat and lon:
            lat = -lat if lat_dir == 'S' else lat
            lon = -lon if lon_dir == 'W' else lon
            return lat, lon
    return None, None

def convert_to_degrees(raw_value):
    """将 NMEA 格式转换为十进制"""
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

def get_google_map(lat, lon, api_key):
    """下载 Google Maps 静态图像"""
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=15&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

def display_map():
    """使用 pygame 在屏幕上显示地图"""
    pygame.init()
    
    # 创建窗口，分辨率 600x400，可修改为树莓派屏幕大小
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("GPS 位置地图")
    
    running = True
    while running:
        try:
            latitude, longitude = get_gps_coordinates()
            print(f"获取成功！LAT: {latitude}, LON: {longitude}")

            map_file = get_google_map(latitude, longitude, API_KEY)
            print("地图更新")

            # 载入图片
            map_image = pygame.image.load(map_file)
            screen.blit(map_image, (0, 0))  # 贴图到窗口
            pygame.display.flip()  # 刷新窗口

            # 3 秒后更新地图
            time.sleep(3)

            # 监听事件，按 ESC 退出
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

        except Exception as e:
            print(f"错误: {str(e)}")
            running = False

    pygame.quit()

if __name__ == "__main__":
    API_KEY = "你的API_KEY"  # 你的 Google Maps API Key
    display_map()
