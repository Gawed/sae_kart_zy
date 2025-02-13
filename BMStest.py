# This script reads the data from a JK BMS over USB-TTL and formats
# Credit to https://github.com/PurpleAlien/jk-bms_grafana

# Instructions:
# Change Serial port on line 17 and run with python3+. Dumps register 0x83 (total pack voltage) to verify BMS communication.
from time import sleep
import time
import sys, os, io
import struct
import paho.mqtt.client as mqtt

# Plain serial... Modbus would have been nice, but oh well. 
import serial

sleepTime = 10

try:
    bms = serial.Serial('/dev/ttyUSB0')
    bms.baudrate = 115200
    bms.timeout  = 0.2
except:
    print("BMS not found.")


# See also: 
# - https://github.com/syssi/esphome-jk-bms
# - https://github.com/NEEY-electronic/JK/tree/JK-BMS
# - https://github.com/Louisvdw/dbus-serialbattery

def sendBMSCommand(cmd):
    sent_cmds = []
    for cmd_byte in cmd:
        hex_byte = ("{0:02x}".format(cmd_byte))
        sent_cmds.append(hex_byte)
        bms.write(bytearray.fromhex(hex_byte))
    return

# This could be much better, but it works.
def readBMS(cmd):
    try: 
        sendBMSCommand(cmd)
        time.sleep(.1)
        if bms.inWaiting() >= 4 :
            output = ""
            available = bms.inWaiting();
            for i in range(available):
                output += bms.read(1).hex() + " "
            
            return output
    except Exception as e:
        print('failed to read bms! Error: ' + str(e))

def byteArrayToHEX(byte_array):
    hex_string = ""
    for cmd_byte in byte_array:
        hex_byte = ("{0:02x}".format(cmd_byte))
        hex_string += hex_byte + " " 

    return hex_string
    
#MAIN() - Query BMS for register 0x83 (pack total voltage)

# See https://diysolarforum.com/resources/jk-bms-documentation-on-protocols-provided-by-hankzor.259/ for protocol specification documents   
def main():
    broker = "192.168.1.88"
    port = 1883
    client = mqtt.Client()    
    client.username_pw_set("mqtt_mat","user")
    client.connect(broker,port,60)

    
    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 85 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/batterie"
    client.publish(topic,message)

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 79 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/single"
    client.publish(topic,message)

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 89 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/capacity"
    client.publish(topic,message)    

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 87 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/time"
    client.publish(topic,message)

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 81 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/box"
    client.publish(topic,message)

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 80 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/tube"
    client.publish(topic,message)    

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 82 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/temperature"
    client.publish(topic,message)    

    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 83 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/tension"
    client.publish(topic,message)


    cmd = bytearray.fromhex('4E 57 00 13 00 00 00 00 03 03 00 84 00 00 00 00 68')
    crc = sum(cmd) #crc is misleading, they really just use the sum of the data so far. 
    cmd += bytearray.fromhex(f'{crc:08x}') #Crazy syntax but this formats the crc decimal value to an 8 character, zero-padded hexadecimal number and then appends it to the original cmd
    output = readBMS(cmd)
    #First find the length bytes
    rawdata = bytearray.fromhex(output)
    length = int.from_bytes(rawdata[2:4], 'big')
    #20 Bytes would be a 1 byte data response. Increase output for bigger 
    result = rawdata[12:(13 + (length-20))] #The returned data starts at pos 12 (byte 13) and varies in size depending on register
    message = str(int.from_bytes(result,'big'))
    topic = "bms/courant"
    client.publish(topic,message)

if __name__ == "__main__" : 
    try : 
            while True :
                    main()
                    sleep(10)
    except Exception as e : 
            print(e)
