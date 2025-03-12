import serial

def parse_gpgga(data):
    """GPGGA """
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

def parse_gpgll(data):
    """ GPGLL """
    parts = data.split(',')
    if len(parts) > 5:
        lat = convert_to_degrees(parts[1]) 
        lat_dir = parts[2]  # N/S
        lon = convert_to_degrees(parts[3])  
        lon_dir = parts[4]  # E/W
        
        if lat and lon:
            lat = -lat if lat_dir == 'S' else lat
            lon = -lon if lon_dir == 'W' else lon
            return lat, lon
    return None, None

def convert_to_degrees(raw_value):
    """ NMEA """
    if not raw_value:
        return None
    try:
        d = int(float(raw_value) / 100)
        m = float(raw_value) - d * 100
        return d + (m / 60)
    except ValueError:
        return None

#  GPS 
ser = serial.Serial('/dev/serial0', baudrate=4800, timeout=1)

while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line.startswith("$GPGGA"):
        lat, lon = parse_gpgga(line)
        if lat and lon:
            print(f"GPGGA : {lat}, {lon}")
    elif line.startswith("$GPGLL"):
        lat, lon = parse_gpgll(line)
        if lat and lon:
            print(f"GPGLL : {lat}, {lon}")
