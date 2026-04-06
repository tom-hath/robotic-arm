
import numpy as np
import time, serial
import socket
ESP_IP = "192.168.28.39"
ESP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
        msg = f"{float(input('x'))},{float(input('y'))},{float(input('z'))}"
        print(msg)
        try:
            sock.sendto(msg.encode(), (ESP_IP, ESP_PORT))
        except Exception as e:
            print("UDP send error:", e)
