import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import BME280
from machine import Pin, I2C, ADC

esp.osdebug(None)
import gc
gc.collect()

ssid = 'IoT_Dev'
password = 'elektro234'
mqtt_server = '192.168.1.150'

client_id = ubinascii.hexlify(machine.unique_id())

topic_pub_temp = 'planter/temperature'
topic_pub_hum = 'planter/humidity'
topic_pub_pres = 'planter/pressure'
topic_pub_analog = 'planter/rain'

last_message = 0
message_interval = 5

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)
bme = BME280.BME280(i2c=i2c)
digital_pin = Pin(5, Pin.IN)
analog_pin = ADC(0)

def connect_mqtt():
  global client_id, mqtt_server
  client = MQTTClient(client_id, mqtt_server)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def read_bme_sensor():
  try:
    temp = '%s' % bme.temperature[:-1]
    hum = '%s' % bme.humidity[:-1]
    pres = '%s'% bme.pressure[:-3]
    return temp, hum, pres
  except OSError as e:
    return('Failed to read sensor.')

def read_rain_sensor():
  try:
    analog_value = analog_pin.read()
    rain = ((-100/1024) * analog_value) + 100
    return rain
  except OSError as e:
    return('Failed to read sensor.')

try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    if (time.time() - last_message) > message_interval:
      temp, hum, pres = read_bme_sensor()
      analog_value = read_rain_sensor()
      print(temp)
      print(hum)
      print(pres)
      print(analog_value)
      client.publish(topic_pub_temp, temp)
      client.publish(topic_pub_hum, hum)      
      client.publish(topic_pub_pres, pres)     
      client.publish(topic_pub_analog, str(analog_value))
      last_message = time.time()
  except OSError as e:
    restart_and_reconnect()
