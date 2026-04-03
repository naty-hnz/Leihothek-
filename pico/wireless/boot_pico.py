import sys
import config
import network
from time import sleep

connection = network.WLAN(network.STA_IF)

def connect():

    if connection.isconnected():
        print("Already connected")
        return

    connection.active(True)
    connection.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    retry = 0
    while not connection.isconnected():
        if retry == 10:
            sys.exit("Could not establish connection, check your settings")
        retry += 1
        print("poging " + str(retry))
        sleep(1)

    print("Connection established")

connect()
