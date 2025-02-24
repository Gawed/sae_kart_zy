import os
import time
import requests
from PIL import Image
import serial

def convert_coordinates(coord, direction):
    """智能坐标转换函数"""
    try:
        # 移除可能存在的多余空格
        coord = coord.strip()
        
        # 根据方向判断是纬度还是经度
        if direction in ['N', 'S']:  # 纬度处理
            deg = float(coord[:2])
            minutes = float(coord[2:])
        else:  # 经度处理
            deg = float(coord[:3])
            minutes = float(coord[3:])
            
        decimal = deg + minutes/60
        return round(decimal * (-1 if direction in ['S','W'] else 1), 6)
    except Exception as e:
        print(f"坐标转换错误: {str(e)}")
        return 0.0, 0.0  # 返回默认值

# 在get_gps_coordinates中添加数据验证
def get_gps_coordinates():
    ser = serial.Serial('/dev/ttyS0', 4800, timeout=1)
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith('$GPGGA'):
                data = line.split(',')
                if len(data) < 7:
                    continue
                
                # 增加数据有效性检查
                if all([data[2], data[3], data[4], data[5]]) and data[6] != '0':
                    lat = convert_coordinates(data[2], data[3])
                    lon = convert_coordinates(data[4], data[5])
                    
                    # 坐标范围验证
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return lat, lon
        except Exception as e:
            print(f"GPS读取错误: {str(e)}")
        time.sleep(0.5)

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
