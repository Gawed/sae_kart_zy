import serial
import time

# 设置串口连接
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

# 假设你的经纬度是：纬度 = 37.7749°N，经度 = -122.4194°W
latitude = 48.2679
longitude = 4.0797

# 创建 GPGGA 语句，设置已知经纬度
# GPGGA 格式：$GPGGA,hhmmss.ss,ddmm.mmmm,N,dddmm.mmmm,W,1,08,0.9,545.4,M,46.9,M,,*47
# 设置经纬度，确保字符串的格式符合 NMEA 标准
gpgga_message = f"$GPGGA,{time.strftime('%H%M%S')},"
gpgga_message += f"{int(latitude)}{int((latitude - int(latitude)) * 60):02.4f},N,"
gpgga_message += f"{int(abs(longitude))}{int((abs(longitude) - int(abs(longitude))) * 60):02.4f},W,"
gpgga_message += "1,08,0.9,545.4,M,46.9,M,,*47"

# 发送 GPGGA 消息到 GPS 模块
ser.write(gpgga_message.encode())

print(f"Sent: {gpgga_message}")
