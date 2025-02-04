import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import gc

esp.osdebug(None)
gc.collect()

ssid = 'IoT_Dev'
password = 'elektro234'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')