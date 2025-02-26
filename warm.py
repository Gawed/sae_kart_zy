import serial
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.write(b'AT+CGNSPVT\r\n')  # u-blox 
