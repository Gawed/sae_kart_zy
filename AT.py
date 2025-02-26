import serial

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.write(b'AT+CGNSPVT\r\n')  # 发送查询定位状态的命令
response = ser.readline().decode('utf-8', errors='ignore')
print(response)
