import serial
import time
import pygame

ser = serial.Serial("/dev/ttyAMA0", 9600, timeout = 15)

def SIM800(command):
    AT_command = command + "\r\n"
    ser.write(str(AT_command).encode('ascii'))
    time.sleep(1)
    if ser.inWaiting() > 0:
        echo = ser.readline() #waste the echo
        response_byte = ser.readline()
        response_str = response_byte.decode('ascii')
        return (response_str)
    else:
        return ("ERROR")

#Checks SIM800L status and connects with ShopifyAPI
def Init_GSM():
    if "OK" in SIM800("AT"):
        if ("OK" in (SIM800("AT+CLCC=1"))) and ("OK" in (SIM800("AT+DDET=1"))) and ("OK" in (SIM800("AT+CNMI =0,0,0,0,0"))) and ("OK" in (SIM800("AT+CMGF=1"))) and ("OK" in (SIM800("AT+CSMP=17,167,0,0"))):  # enble DTMF / disable notifications
            print("SIM800 Module -> Active and Ready")
    else:
        print("------->ERROR -> SIM800 Module not found")

Init_GSM()