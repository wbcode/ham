# from
# VeraArduino/Vera/L_Arduino.lua@0245cd2

import serial
from time import sleep
import logging
import ConfigParser
import time
import datetime
import json
import requests
from Openhab import *
from Domoticz import *
from Rrd import *


class VeraGW():
	
	#supported integrations
	oh = None
	dom = None
	rrd = None

	#supported version
	PLUGIN_VERSION = "1.2+"
	
	GATEWAY_VERSION = ""
	BAUD_RATE = "115200"
	ARDUINO_SID = "urn:upnp-arduino-cc:serviceId:arduino1"
	VARIABLE_CONTAINER_SID = "urn:upnp-org:serviceId:VContainer1"
	MAX_RADIO_ID=255
	NODE_CHILD_ID = "255"
	
	ARDUINO_DEVICE = None
	TASK_ERROR = 2
	TASK_ERROR_PERM = -2
	TASK_SUCCESS = 4
	TASK_BUSY = 1
	inclusionResult = {}
	includeCount = 0
	
	#Variables in Vera can be overridded in config file
	InclusionMode = 0
	unit = "M"
	
	#defines
	msgType = {
        'PRESENTATION' : "0",
        'SET_VARIABLE' : "1",
        'REQ_VARIABLE' : "2",
		'ACK_VARIABLE' : "3",
        'INTERNAL' : "4" }

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
        'LIGHT_LEVEL':[16, "urn:schemas-micasaverde-com:device:LightSensor:1", "D_LightSensor1.xml", "Light "],
		'ARDUINO_NODE': [17, "urn:schemas-arduino-cc:device:arduinonode:1", "D_ArduinoNode1.xml", "Node "],
		'ARDUINO_RELAY':[18, "urn:schemas-arduino-cc:device:arduinorelay:1", "D_ArduinoRelay1.xml", "Relay "],
		'LOCK' : 		  [19, "urn:micasaverde-com:serviceId:DoorLock1", "D_DoorLock1.xml", "Lock "],
		'IR' : 		  [20, "urn:schemas-arduino-cc:device:ArduinoIr:1", "D_ArduinoIr1.xml", "IR "], 
		'WATER' : 	  [21, "urn:schemas-micasaverde-com:device:WaterMeter:1", "D_WaterMeter1.xml", "Water "]
	}

	tVarLookupNumType = {}
	tVarTypes = {
        'TEMP' : 			[0,  "urn:upnp-org:serviceId:TemperatureSensor1", "CurrentTemperature", ""],
	'HUM' : 			[1,  "urn:micasaverde-com:serviceId:HumiditySensor1", "CurrentLevel", "" ],
	'LIGHT' : 		[2,  "urn:upnp-org:serviceId:SwitchPower1", "Status", "0" ],
	'DIMMER' : 		[3,  "urn:upnp-org:serviceId:Dimming1", "LoadLevelStatus", "" ],
	'PRESSURE' : 		[4,  "urn:upnp-org:serviceId:BarometerSensor1", "CurrentPressure", "" ],
	'FORECAST' : 		[5,  "urn:upnp-org:serviceId:BarometerSensor1", "Forecast", "" ],
	'RAIN' : 			[6,  "urn:upnp-org:serviceId:RainSensor1", "CurrentTRain", "" ],
	'RAINRATE' : 		[7,  "urn:upnp-org:serviceId:RainSensor1", "CurrentRain", "" ],
	'WIND' : 			[8,  "urn:upnp-org:serviceId:WindSensor1", "AvgSpeed", "" ],
	'GUST' : 			[9,  "urn:upnp-org:serviceId:WindSensor1", "GustSpeed", "" ],
	'DIRECTION' : 	[10, "urn:upnp-org:serviceId:WindSensor1", "Direction", "" ],
	'UV' : 			[11, "urn:upnp-org:serviceId:UvSensor1", "CurrentLevel", "" ],
	'WEIGHT' : 		[12, "urn:micasaverde-com:serviceId:ScaleSensor1", "Weight", "" ],
	'DISTANCE' : 		[13, "urn:micasaverde-com:serviceId:DistanceSensor1", "CurrentDistance", "" ],
	'IMPEDANCE' : 	[14, "urn:micasaverde-com:serviceId:ScaleSensor1", "Impedance", "" ],
	'ARMED' : 		[15, "urn:micasaverde-com:serviceId:SecuritySensor1", "Armed", "" ],
	'TRIPPED' : 		[16, "urn:micasaverde-com:serviceId:SecuritySensor1", "Tripped", "0" ],
	'WATT' : 			[17, "urn:micasaverde-com:serviceId:EnergyMetering1", "Watts", "" ],
	'KWH' : 			[18, "urn:micasaverde-com:serviceId:EnergyMetering1", "KWH", "0" ],
	'SCENE_ON' : 		[19, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneActivated", "" ],
	'SCENE_OFF' : 	[20, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneDeactivated", "" ],
	'HEATER' : 		[21, "urn:upnp-org:serviceId:HVAC_UserOperatingMode1", "ModeStatus", "" ],
	'HEATER_SW' : 	[22, "urn:upnp-org:serviceId:SwitchPower1", "Status", "" ],
	'LIGHT_LEVEL' : 	[23, "urn:micasaverde-com:serviceId:LightSensor1", "CurrentLevel", "" ],
	'VAR_1' : 		[24, "urn:upnp-org:serviceId:VContainer1", "Variable1", ""],
	'VAR_2' : 		[25, "urn:upnp-org:serviceId:VContainer1", "Variable2", ""],
	'VAR_3' : 		[26, "urn:upnp-org:serviceId:VContainer1", "Variable3", ""],
	'VAR_4' : 		[27, "urn:upnp-org:serviceId:VContainer1", "Variable4", ""],
	'VAR_5' : 		[28, "urn:upnp-org:serviceId:VContainer1", "Variable5", ""],
	'UP' : 		    [29, None, None, ""],
	'DOWN' : 		    [30, None, None, ""],
	'STOP' : 			[31, None, None, ""],
	'IR_SEND' :		[32, None, None, ""],
	'IR_RECEIVE' : 	[33, "urn:upnp-org:serviceId:ArduinoIr1", "IrCode", ""],
	'FLOW' : 			[34, "urn:micasaverde-com:serviceId:WaterMetering1", "Flow", "" ],
	'VOLUME' : 		[35, "urn:micasaverde-com:serviceId:WaterMetering1", "Volume", "0" ],
	'LOCK' : 		    [36, "urn:micasaverde-com:serviceId:DoorLock1", "Status", ""]

	}

	tInternalLookupNumType = {}
	tInternalTypes = {
		"BATTERY_LEVEL" : [0, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryLevel", "" ],
		"BATTERY_DATE" : 	[1, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryDate", "" ],
		"LAST_TRIP" : 	[2, "urn:micasaverde-com:serviceId:SecuritySensor1", "LastTrip", "" ],
		"TIME" : 			[3, None, None, None],
		"VERSION" : 		[4, "urn:upnp-arduino-cc:serviceId:arduinonode1", "ArduinoLibVersion", ""],
		"REQUEST_ID" : 	[5, None, None, None],
		"INCLUSION_MODE" :[6, "urn:upnp-arduino-cc:serviceId:arduino1", "InclusionMode", "0"],
		"RELAY_NODE":     [7, "urn:upnp-arduino-cc:serviceId:arduinonode1", "RelayNode", ""],
		"LAST_UPDATE" : 	[8, "urn:micasaverde-com:serviceId:HaDevice1", "LastUpdate", "" ],
		"PING" : 			[9, None, None, None ],
		"PING_ACK" :      [10, None, None, None ],
		"LOG_MESSAGE" :   [11, None, None, None ],
		"CHILDREN" :  	[12, "urn:upnp-arduino-cc:serviceId:arduinonode1", "Children", "0"],
		"UNIT" :			[13, "urn:upnp-arduino-cc:serviceId:arduino1", "Unit", "M"],  # M : Metric / I : Imperial
		"SKETCH_NAME"    : [14, "urn:upnp-arduino-cc:serviceId:arduinonode1", "SketchName", ""],
	"SKETCH_VERSION" : [15, "urn:upnp-arduino-cc:serviceId:arduinonode1", "SketchVersion", ""]

	}	
	

	#lookup tables
	childIdLookupTable = {}
	availableIds = [True]*254
	
	for k, v in tVarTypes.iteritems():
		tVarLookupNumType[v[0]] = k

	for k, v in tDeviceTypes.iteritems():
		tDeviceLookupNumType[v[0]] = k
	
	for k, v in tInternalTypes.iteritems():
		tInternalLookupNumType[v[0]] = k
	
	
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
			self.processIncoming(response)
			return response
		return None

	def setVariable(self, incomingData, childId, nodeId):
		if (childId is not None) :
			# Set variable reported from a child sensor.
			index = int(incomingData[3]);
			varType = self.tVarLookupNumType[index]
			var = self.tVarTypes[varType]
			value = incomingData[4]
			if (var[1] is not None): 
				self.log.info("setVariable: RaidoId: "+incomingData[0]+" Sensor: "+incomingData[1]+" ChildId: "+str(childId)+" Type: " +self.tVarLookupNumType[index]+" reporting value: "+ value)
				
				#Support integrations			
				# Add info to RRD
				if self.config.has_option('rrds',childId) and self.rrd is not None:
					self.rrd.setVariable(incomingData, childId, nodeId)
				
				# Add info to Domoticz
				if self.config.has_option('domoticz',childId) and self.dom is not None:
					self.dom.setVariable(incomingData, childId, nodeId)
				
				# Add info to Openhab
				if self.config.has_option('openhab',childId) and self.oh is not None:
					self.oh.setVariable(incomingData, childId, nodeId)
				
				self.setVariableIfChanged(var[1], var[2], value, childId)
			
				# Handle special variables battery level and tripped which also
				# should update other variables to os.time(). This part should be removed...
				if (varType == "TRIPPED" and value == "1") :
					variable = self.tInternalTypes["LAST_TRIP"]
					self.setVariableIfChanged(variable[1], variable[2], int(time.time()), childId)

	# Still here since a lot of methods sends info to this one.
	def setVariableIfChanged(self, serviceId, name, value, deviceId):
	
		self.log.info("setVariableIfChanged: "+serviceId +","+name+", "+str(value)+", "+deviceId)
				
#done				
	def nextAvailiableRadioId(self):
		for i in xrange(10,254): 
			if (self.availableIds[i] == True):
				self.availableIds[i] = False
				return i
		return 255
				
#almost done
	def  presentation(self, incomingData, device, childId, altId):
		type = incomingData[3]
		data = incomingData[4]
		mode = self.InclusionMode

		if (mode == 0 and device is None):
			#A new sensor (not created before) was presented during inclusion mode
			if (altId not in self.inclusionResult): 
				self.log.info("presentation: New sensor starting up. Radio: "+ incomingData[0] + " Sensor: "+incomingData[1])
				self.includeCount = self.includeCount+1;
				###check the line below need to do something
				#setVariableIfChanged(ARDUINO_SID, "InclusionFoundCountHR", includeCount .." devices found", ARDUINO_DEVICE)
				#calc and write to config file.
				
				#Find max current childId add one for the new sensor.
				# not nice but this is how I try to learn python, 5 years from now I will cry over this solution.
				index = -1
				for k, v in self.config.items("childIds") :
					if int(k) > index :
						index = int(k)
				
				index += 1
				
				self.childIdLookupTable[altId] = index
				self.config.set('childIds',str(index),altId+";"+type)
				
				with open('VeraGW.conf', 'wb') as configfile:
					self.config.write(configfile)
				
				self.inclusionResult[altId] = type
			elif (mode == 0 and device is not None and childId == self.NODE_CHILD_ID and data != self.GATEWAY_VERSION):
				#The library version of sensor differs from plugin version. Warn about it.
				self.log.warn("presentation: Doesn't match Gateway version("+self.GATEWAY_VERSION+ "). Radio: "+ incomingData[0] + " Sensor: "+incomingData[1] + " using version: " + incomingData[4])

#done is going to need a lot of work...					
	def processInternalMessage(self, incomingData, iChildId, iAltId):
		data = incomingData[4]
		index = int(incomingData[3]);
		varType = self.tInternalLookupNumType[index]
		var = self.tInternalTypes[varType]
	
		if (varType == "VERSION" and iAltId == "0;0"):
			#Store version of Arduino Gateway
			self.GATEWAY_VERSION = data
			self.log.info('processInternalMessage: Gateway running version: '+self.GATEWAY_VERSION )
			print("Connected to Mysensor Gateway running version %s" % data)
		elif ((varType == "SKETCH_NAME" or varType == "SKETCH_VERSION") and iChildId is not None) :
			# Store the Sketch name and Version
			v = self.config.get('childIds',str(iChildId))
			d = v.split(";")
			name = d[2]
			version = d[2]
			if varType == "SKETCH_NAME" : 
				name = data.rstrip()
			elif varType == "SKETCH_VERSION" :
				version = data.rstrip()
			
			self.config.set('childIds',str(iChildId),iAltId+";"+name+";"+version)
			
			with open('VeraGW.conf', 'wb') as configfile:
				self.config.write(configfile)

		elif (varType == "TIME"):
			#Request time was sent from one of the sensors
			self.sendInternalCommand(iAltId,"TIME",time.time())
		elif (varType == "UNIT"):
			#Request for unit was sent from one of the sensors
			self.sendInternalCommand(iAltId,"UNIT",self.unit)
		elif (varType == "REQUEST_ID"):
			#Determine next available radioid and sent it to the sensor
			self.sendInternalCommand(iAltId,"REQUEST_ID",self.nextAvailiableRadioId())
		elif (varType == "RELAY_NODE" and iChildId is not None):
			#Set human readable relay mode status
			self.setVariableIfChanged(var[1], var[2], data, iChildId)
			### Have a look at the one below
			#setVariableIfChanged(var[1], "RelayNodeHR", data == "0" and "GW" or data, iChildId)
		elif (varType == "BATTERY_LEVEL"):
		# Send to serVariable since you usally want to store this info.
			self.setVariable(incomingData, iChildId, iAltId)			
		elif (varType == "INCLUSION_MODE"):
			self.setVariableIfChanged(var[1], var[2], data, ARDUINO_DEVICE)
			if (data == "0") :
				self.setVariableIfChanged(ARDUINO_SID, "InclusionFoundCountHR", "", ARDUINO_DEVICE)
				inclusionCount = 0
				#Here comes the presentation data from sensors
				newDevices = 0
				#check type of this variable
				child_devices
				self.log.info("processInternalMessage: Inclusion mode ended.")

				for altId, deviceType in inclusionResult.iteritems():
					childId = self.childIdLookupTable[altId] 
					if (childId == None): 
						deviceId = self.tDeviceLookupNumType[int(deviceType)]
						if (deviceId != None):		
							splitted = altId.split(";")
							nodeId = splitted[0]
							childId = splitted[1]
							#Check this empty variable
							name

							#A new child sensor has been found. Create it!
							deviceType = tDeviceTypes[deviceId]
							#Create device if device sent presentation
							if (newDevices == 0):
								#check this creates a new device
								child_devices = luup.chdev.start(ARDUINO_DEVICE)
							
							if (childId == self.NODE_CHILD_ID):
								name = nodeId
							else:
								name = nodeId + ":" + childId
							
							#append newly found sensor device
							#check below here we add new devices...
							#luup.chdev.append(ARDUINO_DEVICE, child_devices, altId, "Arduino " .. deviceType[4]..name, deviceType[2],deviceType[3],"","",false)
							newDevices = newDevices + 1		
						else:
							self.log.error("processInternalMessage: Found unknown device type " + deviceType +". Inclusion aborted. Please try again.")
							newDevices = -100
					else :
						self.log.info("processInternalMessage: Device "+altId+" already exists.")
			else:
				self.setVariableIfChanged(ARDUINO_SID, "InclusionFoundCountHR", "0 devices found", ARDUINO_DEVICE)

		elif (varType == "CHILDREN"):
			self.setVariableIfChanged(var[1], var[2], data, iChildId)
		elif (varType == "LOG_MESSAGE"):
			self.log.info("processInternalMessage: Log message:" + data)
		else:
			self.log.info("processInternalMessage: Incoming internal command discarded:" + data)
					
	def sendCommandOne(self,cmd):
		if self.ser.writable:
 			self.ser.write(cmd+"\n")
			self.log.debug("sendCommandOne: Sending: "+cmd)
		else:
			self.log.error("sendCommandOne: Can't write to serial port")

	def setUnit(unit): 
		self.setVariableIfChanged(ARDUINO_SID, "Unit", unit, ARDUINO_DEVICE)
		
			
#done			
	# Function to send a message to sensor
	def sendCommand(self, altid, variableId, value):
		return self.sendCommandWithMessageType(altid, "SET_VARIABLE", int(tVarTypes[variableId][0]), value)
#done	
	def sendNodeCommand(self, device, variableId, value):
		return self.sendCommandWithMessageType(device+";255", "SET_VARIABLE", int(tVarTypes[variableId][0]), value)
#done	
	def sendInternalCommand(self, altid, variableId, value):
		return self.sendCommandWithMessageType(altid, "INTERNAL", int(self.tInternalTypes[variableId][0]), str(value))
#done	
	def sendRequestResponse(self, altid, variableId, value):
		return self.sendCommandWithMessageType(altid, "ACK_VARIABLE", int(self.tVarTypes[variableId][0]), value)
		
#done	
	def sendCommandWithMessageType(self, altid, messageType, variableId, value):
		cmd = altid+";"+self.msgType[messageType]+";"+str(variableId)+";"+value+"\n"
		if self.ser.writable:
 			self.ser.write(cmd)
			self.log.debug("sendCommandWithMessageType: Sending: "+cmd)
			return True
		else:
			self.log.error("sendCommandWithMessageType: Can't write to serial port")
			return False

#done
	def processIncoming(self, s):
		self.log.info("processIncoming: Receiving: "+s)
		incomingData = s.split(';')
		if len(incomingData) >= 4:
			nodeId = incomingData[0]
			childId = incomingData[1]
			messageType = incomingData[2]
			altId = nodeId+";"+childId
			if altId in self.childIdLookupTable :
				device = self.childIdLookupTable[altId] 
			else :
				device = None

			if messageType==self.msgType["SET_VARIABLE"]:
				self.setVariable(incomingData, device, nodeId)
			elif messageType == self.msgType["PRESENTATION"]:
				self.presentation(incomingData, device, childId, altId)
			elif messageType == self.msgType["REQ_VARIABLE"]:
				self.requestStatus(incomingData, device, altId)
			elif messageType == self.msgType["INTERNAL"]:
				self.processInternalMessage(incomingData, device, altId)
			else:
				self.log.error("processIncoming: Error: Classic you shouldn't end up here: "+ s)
		else:
			self.log.error("processIncoming: Error: Receive unknown data: "+ s)

	def requestStatus(self, incomingData, childId, altId):
		self.log.debug("Requesting status for: "+altId)
		#A device request its current status from vera (when staring up)
		index = int(incomingData[3])	
		varType = self.tVarLookupNumType[index]
		
		#Requested variable value from one of the sensors 
		variable = self.tVarTypes[varType]
		if (variable[2] is not None and childId is not None): 
			value = None
			self.log.debug("Request status for "+ variable[2])
			
			#openhab
			if self.config.has_option('openhab',childId) and self.oh is not None:
				oh = Openhab(self.config, self.log)
				value=self.oh.requestStatus(incomingData, childId, altId)
			#support others here like Domoticz
	

			#Get default if there is none in the external system
			if	value is None :
				self.sendRequestResponse(altId,varType,variable[3])
			else :
				self.sendRequestResponse(altId,varType,value)
			
	#Arduino GW device commands
	def startInclusion(device):
		return sendInternalCommand("0;0","INCLUSION_MODE","1")


	def stopInclusion(device):
		return sendInternalCommand("0;0","INCLUSION_MODE","0")

			
	#Arduino relay node device commands
	def fetchChildren(self, device):
		variable = self.tInternalTypes["CHILDREN"]
		self.setVariableIfChanged(variable[1], variable[2], "Fetching...", device)
		#self.sendInternalCommand(luup.devices[device].id,"CHILDREN","F")
		self.sendInternalCommand(luup.devices[device].id,"CHILDREN","F")

	def clearChildren(self, device):
		variable = self.tInternalTypes["CHILDREN"]
		self.setVariableIfChanged(variable[1], variable[2], "Clearing...", device)
		#self.sendInternalCommand(luup.devices[device].id,"CHILDREN","C")
		self.sendInternalCommand(device+";255","CHILDREN","C")

	def refreshRelay(self, device):
		variable = self.tInternalTypes["RELAY_NODE"]
		self.setVariableIfChanged(variable[1], variable[2], "Refreshing...", device)
		#self.sendInternalCommand(luup.devices[device].id,"RELAY_NODE","")
		self.sendInternalCommand(device+";255","RELAY_NODE","")
		
	def windowCovering(self, device, action):
		#self.sendCommand(luup.devices[device].id,action,"")
		self.sendCommand(device+";255",action,"")
					
	# Power and dimmer commands
	def switchPower(self, device, newTargetValue):
		self.sendCommand(luup.devices[device].id,"LIGHT",newTargetValue)

	def sendIrCommand(self, device, irCodeNumber):
		self.sendCommand(luup.devices[device].id,"IR_SEND",irCodeNumber)

	def setDimmerLevel(self, device, newLoadlevelTarget):
		self.sendCommand(luup.devices[device].id,"DIMMER",newLoadlevelTarget)

	def setLockStatus(device, newTargetValue) :
		sendCommand(luup.devices[device].id,"LOCK",newTargetValue)
		
	# Security commands
	def setArmed(self, device, newArmedValue):
		self.setVariableIfChanged(tVarTypes.ARMED[2], tVarTypes.ARMED[3], newArmedValue, device)

		
	def updateLookupTables(self, radioId, childId, deviceId):
		self.childIdLookupTable[radioId+";"+childId] = deviceId
		self.availableIds[radioId] = False

	### Support functions 	
	def reloadConfig(self) :
		#load known sensors from file
		for k, v in self.config.items("childIds") :
			value = v.split(';')
			self.childIdLookupTable[value[0]+";"+value[1]] = k
			self.availableIds[int(value[0])]=False
		
		#load unit M/I from file (A good programmer should check input values)
		self.unit = self.config.get('config','unit')
		
		#load unit InclutionMode from file (A good programmer should check input values...)
		self.InclutionMode = int(self.config.get('config','inclusion-mode'))
		
		#initiate integrations
		#Openhab
		if self.config.get('config','openhab') == 'true':
			if self.oh is None :
				self.oh = Openhab(self.config, self.log)
			else :
				self.oh.reloadConfig()
		else :
			self.oh = None
			
		#Domoticz
		if self.config.get('config','domoticz') == 'true':
			if self.dom is None :
				self.dom = Domoticz(self.config, self.log)
			else :
				self.dom.reloadConfig()
		else :
			self.dom = None
		
		#RRD
		if self.config.get('config','rrd') == 'true':
			if self.rrd is None :
				self.rrd = Rrd(self.config, self.log)
			else :
				self.rrd.reloadConfig()
		else :
			self.rrd = None
		
		self.log.info("reloadConfig: Configuration reloaded.")
		
		
	
	#Parse command from external GUI:s like Openhab move this to Openhab file
	def parseExternalCommand(self,external,name,type,state) :
		#Openhab support
		if external == "OpenHab" and self.oh is not None:
			value=self.oh.parseCommand(type,state)
			childId = self.oh.getChildIdFromNane(name)
			if value is not None and childId is not None :
				device = self.config.get('childIds',childId)
				action=self.msgType["SET_VARIABLE"]
				self.sendCommandOne(device+";"+value+'\n')
			else :	
				self.log.error("parseExternalCommand: Missing value to send")
		#elif external == "Domoticz" ....
			#Write the code to support Domoticz
		else :
			self.log.error("parseExternalCommand: Don't support external commands for type: "+ external)
		
	#main
	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig
	
		self.reloadConfig()
		
		#open serial interface 
		self.ser = serial.Serial(self.config.get('config','port'),self.config.get('config','baudrate'),timeout=1)
		self.log.info("Start up: Listening on :" + self.config.get('config','port') +" using baudrate: "+ self.config.get('config','baudrate') )
		self.ser.close()
		self.ser.open()
		
		print("Using Serial port %s at baudrate %s" % (self.config.get('config','port'), self.config.get('config','baudrate')))
		
		#Give Arduino time to start up.
		sleep(5)
		self.sendCommandWithMessageType("0;0","INTERNAL",int(self.tInternalTypes["VERSION"][0]),"Get Version")
