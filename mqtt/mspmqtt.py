#! /usr/bin/python2.7
from MySensor import MySensor
import ConfigParser
import logging
import socket
import paho.mqtt.client as mqtt
import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import serial
from time import sleep


class mspmqtt(threading.Thread):
	def __init__(self, log=None, config=None):
		threading.Thread.__init__(self)
		self.log=log
		self.config=config
		

		#Get values from config
		
		self.mysensor_ip = self.config.get('config','mysensor_ip')
		self.mysensor_port = self.config.get('config','mysensor_port')
		self.http_ip = self.config.get('config','http_ip')
		self.http_port = self.config.get('config','http_port')
		self.mqtt_ip = self.config.get('config','mqtt_ip')
		self.mqtt_port = self.config.get('config','mqtt_port')
		self.serial_port = self.config.get('config','serial_port')
		self.serial_baudrate = self.config.get('config','serial_baudrate')
		self.base_topic = self.config.get('config','mqtt_topic')
		
		# Constants
		self.BUFFER_SIZE = 48		
		
		#Variables
		s = None
		client = None
		self.ser = serial.Serial(self.serial_port,self.serial_baudrate,timeout=1)
		
		#open serial interface 
		self.log.info("Start up: Listening on :" + self.serial_port +" using baudrate: "+ self.serial_baudrate) 
		self.ser.close()
		self.ser.open()
		
		print("Using Serial port %s at baudrate %s" % (self.serial_port, self.serial_baudrate))
		
		#Give Arduino time to start up.
		sleep(5)

		self.client = mqtt.Client(protocol=3)
		self.client.on_message = self.on_message
		self.client.on_connect = self.on_connect
			
		#self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.mysensor = MySensor(self.log,self.config,self.ser,self.client)

	#mqtt
	def on_connect(self,client, userdata, flags, rc):
		print("Connected with result code "+str(rc))
		self.client.subscribe(self.base_topic+"#")		
	#mqtt
	def on_message(self,client, userdata, msg):
		self.mysensor.processMqttMessage(msg)
		print(msg.topic+" "+str(msg.payload))
		
	
		

	#def on_publish(self,client, userdata, msg):
	#	print(msg.topic+" "+str(msg.payload))
	
	def run(self):
		#check if we can handle reconnect in some why.
		#self.s.settimeout( 5.0)
		#self.s.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		#self.s.connect((self.mysensor_ip, int(self.mysensor_port)))
		self.client.connect(self.mqtt_ip, int(self.mqtt_port), 60)
		self.client.loop_start()
		
		self.client.publish(self.base_topic,"startup")
		
		
		while 1 :
			print self.mysensor.loop()
	

''' WEB server'''
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
		self.send_response(200)
		self.end_headers()
		message =  threading.currentThread().getName()
		#self.wfile.write(message)
		self.wfile.write('<html><title>msomqtt gateway</title><body><h2>Configuration</h2><h3>MQTT</h3>')
		self.wfile.write('<p>Broker: '+self.mqtt_ip+'<br>')
		self.wfile.write('Port: '+self.mqtt_port+'</p>')
		self.wfile.write('\n')
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class WWWServer(threading.Thread):
	server = None
	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		server = ThreadedHTTPServer(('10.10.11.126', 8080), Handler)
		print 'Starting server, use <Ctrl-C> to stop'
		server.serve_forever()
	
''' MAIN '''	
			
if __name__ == '__main__':

	#read config file
	config = ConfigParser.ConfigParser()
	config.read("mspmqtt.conf")

	# Setup logging
	log = logging.getLogger('mspmqtt')
	hdlr = logging.FileHandler(config.get('config','log_file'))
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	log.addHandler(hdlr)
	if config.get('config', 'debug'):
		log.setLevel(logging.DEBUG)
	else:
		log.setLevel(logging.NOTICE)
	
	#create gateway object
	mspmqtt = mspmqtt(log,config)
	#create server object
	www = WWWServer()
	
	#start threads
	mspmqtt.start()			
	www.start()
	
	print 'Starting server, use <Ctrl-C> to stop'


	

