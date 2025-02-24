import os
import time
import requests
from PIL import Image
import serial

def get_gps_coordinates():
    # 直接读取串口数据
    ser = serial.Serial('/dev/ttyS0', 4800, timeout=1)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPGGA'):
            data = line.split(',')
            if data[6] != '0':  # 检查定位状态
                lat = convert_coordinates(data[2], data[3])  # 纬度
                lon = convert_coordinates(data[4], data[5]) # 经度
                return lat, lon
        time.sleep(0.5)

def convert_coordinates(coord, direction):
    """
    修正 GPS 坐标格式转换：
    - 纬度 (lat) 格式: DDMM.MMMM
    - 经度 (lon) 格式: DDDMM.MMMM
    """
    if not coord or coord == '':
        return None
    
    # 判断是纬度还是经度
    if len(coord) > 5:  # 纬度是 DDMM.MMMM，经度是 DDDMM.MMMM
        deg_len = 2 if direction in ['N', 'S'] else 3  # 纬度前两位是度，经度前三位是度
        deg = float(coord[:deg_len])
        minutes = float(coord[deg_len:])
    else:
        return None  # 解析错误，返回 None

    # 计算十进制格式
    decimal = deg + (minutes / 60)

    # 南纬（S）或西经（W）需要取负数
    if direction in ['S', 'W']:
        decimal *= -1

    return round(decimal, 8)  # 保留8位小数，提高精度

def get_google_map(lat, lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=15&size=600x400&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={api_key}"
    response = requests.get(url)
    with open('map.png', 'wb') as f:
        f.write(response.content)
    return 'map.png'

if __name__ == "__main__":
    API_KEY = "AIzaSyDLvUcraTLttRBcvn728IaGCe_prAZK24Q"  # 替换为你的API密钥
    
    try:
        print("等待GPS定位...")
        latitude, longitude = get_gps_coordinates()
        print(f"坐标获取成功！纬度: {latitude}, 经度: {longitude}")
        
        map_file = get_google_map(latitude, longitude, API_KEY)
        
        # 显示地图图像
        img = Image.open(map_file)
        img.show()
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
