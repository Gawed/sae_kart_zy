import serial

def parse_gpgga(data):
    """解析 GPGGA 语句，提取经纬度"""
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

def parse_gpgll(data):
    """解析 GPGLL 语句，提取经纬度"""
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[1])  # 纬度
        lat_dir = parts[2]  # N/S
        lon = convert_to_degrees(parts[3])  # 经度
        lon_dir = parts[4]  # E/W
        
        if lat and lon:
            lat = -lat if lat_dir == 'S' else lat
            lon = -lon if lon_dir == 'W' else lon
            return lat, lon
    return None, None

def convert_to_degrees(raw_value):
    """将 NMEA 坐标转换为十进制度"""
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

# 打开 GPS 串口
ser = serial.Serial('/dev/serial0', baudrate=4800, timeout=1)

while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line.startswith("$GPGGA"):
        lat, lon = parse_gpgga(line)
        if lat and lon:
            print(f"GPGGA 经纬度: {lat}, {lon}")
    elif line.startswith("$GPGLL"):
        lat, lon = parse_gpgll(line)
        if lat and lon:
            print(f"GPGLL 经纬度: {lat}, {lon}")
