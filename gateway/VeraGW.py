import serial
from time import sleep
import logging
import ConfigParser
import rrdtool
from pymongo import MongoClient
import datetime

class VeraGW():

	#supported version
	plugin_version ="1.2"
	
	#defines
	msgType = {
        'SENSOR_PRESENTATION' : "0",
        'SET_VARIABLE' : "1",
        'REQUEST_STATUS' : "2",
        'MESSAGE' : "99" }

	tDeviceLookupNumType = {}
	tDeviceTypes = {
        'DOOR' :                [0,  "urn:schemas-micasaverde-com:device:DoorSensor:1", "D_DoorSensor1.xml", "Door "],
        'MOTION' :      [1,  "urn:schemas-micasaverde-com:device:MotionSensor:1", "D_MotionSensor1.xml", "Motion "],
        'SMOKE' :       [2,  "urn:schemas-micasaverde-com:device:SmokeSensor:1", "D_SmokeSensor1.xml", "Smoke "],
        'LIGHT' :       [3,  "urn:schemas-upnp-org:device:BinaryLight:1", "D_BinaryLight1.xml", "Light "],
        'DIMMER' :      [4,  "urn:schemas-upnp-org:device:DimmableLight:1", "D_DimmableLight1.xml", "Dim Light "],
        'COVER' :       [5,  "urn:schemas-micasaverde-com:device:WindowCovering:1", "D_WindowCovering1.xml", "Window " ],
        'TEMP' :                [6,  "urn:schemas-micasaverde-com:device:TemperatureSensor:1", "D_TemperatureSensor1.xml", "Temp "],
        'HUM' :                 [7,  "urn:schemas-micasaverde-com:device:HumiditySensor:1", "D_HumiditySensor1.xml", "Humidity "],
        'BARO' :                [8,  "urn:schemas-micasaverde-com:device:BarometerSensor:1", "D_BarometerSensor1.xml", "Baro "],
        'WIND' :                [9,  "urn:schemas-micasaverde-com:device:WindSensor:1", "D_WindSensor1.xml", "Wind "],
        'RAIN' :                [10, "urn:schemas-micasaverde-com:device:RainSensor:1", "D_RainSensor1.xml", "Rain "],
        'UV' :          [11, "urn:schemas-micasaverde-com:device:UvSensor:1", "D_UvSensor1.xml", "UV "],
        'WEIGHT' :      [12, "urn:schemas-micasaverde-com:device:ScaleSensor:1", "D_ScaleSensor1.xml", "Weight "],
        'POWER' :       [13, "urn:schemas-micasaverde-com:device:PowerMeter:1", "D_PowerMeter1.xml", "Power "],
        'HEATER' :      [14, "urn:schemas-upnp-org:device:Heater:1", "D_Heater1.xml", "Heater "],
        'DISTANCE' :    [15, "urn:schemas-upnp-org:device:Distance:1", "D_DistanceSensor1.xml", "Distance "],
        'LIGHT_LEVEL':[16, "urn:schemas-micasaverde-com:device:LightSensor:1", "D_LightSensor1.xml", "Light "]
	}

	tVarLookupNumType = {}
	tVarTypes = {
        'TEMP' :                        [0,  "urn:upnp-org:serviceId:TemperatureSensor1", "CurrentTemperature", ""],
        'HUM' :                         [1,  "urn:micasaverde-com:serviceId:HumiditySensor1", "CurrentLevel", "" ],
        'LIGHT' :               [2,  "urn:upnp-org:serviceId:SwitchPower1", "Status", "0" ],
        'DIMMER' :              [3,  "urn:upnp-org:serviceId:Dimming1", "LoadLevelStatus", "" ],
        'PRESSURE' :            [4,  "urn:upnp-org:serviceId:BarometerSensor1", "CurrentPressure", "" ],
        'FORECAST' :            [5,  "urn:upnp-org:serviceId:BarometerSensor1", "Forecast", "" ],
        'RAIN' :                        [6,  "urn:upnp-org:serviceId:RainSensor1", "CurrentTRain", "" ],
        'RAINRATE' :            [7,  "urn:upnp-org:serviceId:RainSensor1", "CurrentRain", "" ],
        'WIND' :                        [8,  "urn:upnp-org:serviceId:WindSensor1", "AvgSpeed", "" ],
        'GUST' :                        [9,  "urn:upnp-org:serviceId:WindSensor1", "GustSpeed", "" ],
        'DIRECTION' :   [10, "urn:upnp-org:serviceId:WindSensor1", "Direction", "" ],
        'UV' :                  [11, "urn:upnp-org:serviceId:UvSensor1", "CurrentLevel", "" ],
        'WEIGHT' :              [12, "urn:micasaverde-com:serviceId:ScaleSensor1", "Weight", "" ],
        'DISTANCE' :            [13, "urn:micasaverde-com:serviceId:DistanceSensor1", "CurrentDistance", "" ],
        'IMPEDANCE' :   [14, "urn:micasaverde-com:serviceId:ScaleSensor1", "Impedance", "" ],
        'BATTERY_LEVEL' : [15, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryLevel", "" ],
        'BATTERY_DATE' :        [16, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryDate", "" ],
        'ARMED' :               [17, "urn:micasaverde-com:serviceId:SecuritySensor1", "Armed", "" ],
        'TRIPPED' :             [18, "urn:micasaverde-com:serviceId:SecuritySensor1", "Tripped", "0" ],
        'LAST_TRIP' :   [19, "urn:micasaverde-com:serviceId:SecuritySensor1", "LastTrip", "" ],
        'WATT' :                        [20, "urn:micasaverde-com:serviceId:EnergyMetering1", "Watts", "" ],
        'KWH' :                         [21, "urn:micasaverde-com:serviceId:EnergyMetering1", "KWH", "0" ],
        'SCENE_ON' :            [22, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneActivated", "" ],
        'SCENE_OFF' :   [23, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneDeactivated", "" ],
        'HEATER' :              [24, "urn:upnp-org:serviceId:HVAC_UserOperatingMode1", "ModeStatus", "" ],
        'HEATER_SW' :   [25, "urn:upnp-org:serviceId:SwitchPower1", "Status", "" ],
        'LIGHT_LEVEL' :         [26, "urn:micasaverde-com:serviceId:LightSensor1", "CurrentLevel", "" ],
        'VAR_1' :               [27, "urn:upnp-org:serviceId:VContainer1", "Variable1", ""],
        'VAR_2' :               [28, "urn:upnp-org:serviceId:VContainer1", "Variable2", ""],
        'VAR_3' :               [29, "urn:upnp-org:serviceId:VContainer1", "Variable3", ""],
        'VAR_4' :               [30, "urn:upnp-org:serviceId:VContainer1", "Variable4", ""],
        'VAR_5' :               [31, "urn:upnp-org:serviceId:VContainer1", "Variable5", ""],
        'TIME' :                        [32, None, None, None],
        'VERSION' :             [33, "urn:upnp-org:serviceId:VContainer1", "ArduinoLibVersion", ""],
        'REQUEST_ID' :  [34, None, None, None]
	}

	childIdLookupTable = {}
	availableIds = [True]*254

	#lookup tables
	for k, v in tVarTypes.iteritems():
		tVarLookupNumType[v[0]] = k

	for k, v in tDeviceTypes.iteritems():
		tDeviceLookupNumType[v[0]] = k
	#poor mans hook.
	def hooking(self,incomingData,ChildId) :
		index = int(incomingData[3]);
                variable = self.tVarTypes[self.tVarLookupNumType[index]]
                value = incomingData[4].strip()
		if int(ChildId) == 3 :
			f = open('/usr/share/nginx/www/info.dat', 'w')
			f.write(value)
			f.close()

	def loop(self):
		response = self.ser.readline()
		if response:
			self.log.debug("loop: Incomming message: "+response)
			self.parseIncoming(response)
			return response
		return None
                
	def setVariable(self, incomingData, childId):
		if childId is not None:
			index = int(incomingData[3]);
			variable = self.tVarTypes[self.tVarLookupNumType[index]]
			value = incomingData[4].strip()
			if variable[1] is not None:
				self.log.info("setVariable: RaidoId: "+incomingData[0]+" Sensor: "+incomingData[1]+" ChildId: "+childId+" Type: " +self.tVarLookupNumType[index]+" reporting value: "+ value)
				post = { "childid": childId,
		     			 "value": value,
		     			 "type": incomingData[3],
		     			 "time": datetime.datetime.utcnow()}
				#poor mans hook if you know how to hook this can be done better.
				self.hooking(incomingData, childId)
	
				posts = self.db.sd
				post_id = posts.insert(post)

	def sensorPresentation(self, incomingData, childId, altId):
		if childId is None and altId != "0;0":
			if int(incomingData[3]) in self.tDeviceLookupNumType:
				deviceId = self.tDeviceLookupNumType[int(incomingData[3])]
			else:
				deviceId = None
        # Add code to handle new devices or new sensores on all ready know radio ids:
				self.log.warn("sensorPresentation : Warning: Doesn't support unknown devices. Data: "+incomingData)
		elif childId is not None :
			# Known sensor starting up.
			self.log.info("sensorPresentation: Known sensor starting up. Radio: "+ incomingData[0] + " Sensor: "+incomingData[1])
			if incomingData[4].strip() != "" and incomingData[4].strip() != self.gateway_version:
				self.log.warn("sensorPresentation: Doesn't match Gateway version("+self.gateway_version+ "). Radio: "+ incomingData[0] + " Sensor: "+incomingData[1] + " using version: " + incomingData[4])

	def processMessage(self, inData):
		m_data = inData.split('=')
		if m_data[0] == "version":
			self.log.info("processMessage: Arduino Vera Gateway version: "+m_data[1])
			self.gateway_version = m_data[1].strip()
		elif m_data[0] == "message":
			self.log.info("processMessage: Message: "+m_data[1])
		elif m_data[0] == "error":
			self.log.error("processMessage: Error: "+m_data[1])
		else:
			self.log.info("processMessage: Message: "+m_data[3])

	def sendCommandOne(self,cmd):
		if self.ser.writable:
 			print self.ser.write(cmd+"\n")
			self.log.debug("sendCommand: Sending: "+cmd)
		else:
			self.log.error("sendCommandOne: Can't write to serial port")
			
	def sendCommand(self, altid, variableId, value):
		cmd = altid+";"+str(self.tVarTypes[variableId][0])+";"+value+"\n"
		if self.ser.writable:
 			print self.ser.write(cmd)
			self.log.debug("sendCommand: Sending: "+cmd)
		else:
			self.log.error("sendCommand: Can't write to serial port")

	def parseIncoming(self, res):
		print res
		m_res = res.split(';')
		print m_res
		print self.childIdLookupTable
		if len(res) >= 3:
			m_radioId = m_res[0]
			m_childSendorId = m_res[1]
			m_messageType = m_res[2]
			m_altId = m_radioId+";"+m_childSendorId
			if m_altId in self.childIdLookupTable:
				m_childId = self.childIdLookupTable[m_altId]
			else:
				m_childId = None

			print ("RADIO ID: " +str(m_radioId)+ " CHILD ID: "+str(m_childSendorId)+ " MESSAGE TYPE :" +str(m_messageType))
			if m_messageType == self.msgType["SENSOR_PRESENTATION"]:
				self.sensorPresentation(m_res, m_childId, m_altId)
			elif m_messageType == self.msgType["SET_VARIABLE"]:
				self.setVariable(m_res, m_childId)
			elif m_messageType == self.msgType["REQUEST_STATUS"]:
				print ("request variable")
			elif m_messageType == self.msgType["MESSAGE"]:
				self.processMessage(m_res[4])
			else:
				print ("something else")
		else:
			self.log.error("parseIncoming: Error: Receive unknown data: "+ res)


	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig

		#database
		self.log.info("Connecting to database")
		self.client = MongoClient(self.config.get('database','host'), int(self.config.get('database','port')))
		self.db = self.client[self.config.get('database','db')]
		self.log.info("Init serial interface")		
		
		#load known sensors from file
		for k, v in self.config.items("childIds") :
			self.childIdLookupTable[v] = k
			self.availableIds[int(v.split(';')[0])]=False
		
		self.ser = serial.Serial(self.config.get('config','port'),self.config.get('config','baudrate'),timeout=1)
		self.log.info("Start up: Listening on :" + self.config.get('config','port') +" using baudrate: "+ self.config.get('config','baudrate') )
		self.ser.close()
		self.ser.open()
		#Give Arduino time to start up.
		sleep(5)
		self.sendCommand("0;0","VERSION","Get Version")
