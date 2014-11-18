
class MySensor():
	def __init__(self,log,config, ser, client, sock=None):
		self.atoms = []
        
		self.log=log
		self.config=config
		self.sock=sock
		self.ser=ser
		self.client = client
		
		self.PLUGIN_VERSION = "1.4"
		self.GATEWAY_VERSION = ""
		self.NODE_CHILD_ID="255"
		self.MAX_RADIO_ID=255
		
		self.childIdLookupTable = {}
		self.availableIds = [True]*254
		
		#config values
		self.unit = None
		self.InclusionMode = None
		self.mysensor_ip = None
		self.mysensor_port = None
		
		self.inclusionResult = {}
		self.includeCount = 0
		
		self.last_message = None
		self.last_topic = None
		
		self.msgType = {
                'PRESENTATION' : '0',
                'SET' : '1',
                'REQUEST' : '2',
                'INTERNAL' : '3',
                'STREAM' : '4'
		}

		self.tDeviceTypes = {
				'S_DOOR': [0, "urn:schemas-micasaverde-com:device:DoorSensor:1", "D_DoorSensor1.xml", "Door "],
				'S_MOTION': [1, "urn:schemas-micasaverde-com:device:MotionSensor:1", "D_MotionSensor1.xml", "Motion "],
				'S_SMOKE': [2, "urn:schemas-micasaverde-com:device:SmokeSensor:1", "D_SmokeSensor1.xml", "Smoke "],
				'S_LIGHT': [3, "urn:schemas-upnp-org:device:BinaryLight:1", "D_BinaryLight1.xml", "Light "],
				'S_DIMMER': [4, "urn:schemas-upnp-org:device:DimmableLight:1", "D_DimmableLight1.xml", "Dim Light "],
				'S_COVER': [5, "urn:schemas-micasaverde-com:device:WindowCovering:1", "D_WindowCovering1.xml", "Window " ],
				'S_TEMP': [6, "urn:schemas-micasaverde-com:device:TemperatureSensor:1", "D_TemperatureSensor1.xml", "Temp "],
				'S_HUM': [7, "urn:schemas-micasaverde-com:device:HumiditySensor:1", "D_HumiditySensor1.xml", "Humidity "],
				'S_BARO': [8, "urn:schemas-micasaverde-com:device:BarometerSensor:1", "D_BarometerSensor1.xml", "Baro "],
				'S_WIND': [9, "urn:schemas-micasaverde-com:device:WindSensor:1", "D_WindSensor1.xml", "Wind "],
				'S_RAIN': [10, "urn:schemas-micasaverde-com:device:RainSensor:1", "D_RainSensor1.xml", "Rain "],
				'S_UV': [11, "urn:schemas-micasaverde-com:device:UvSensor:1", "D_UvSensor1.xml", "UV "],
				'S_WEIGHT': [12, "urn:schemas-micasaverde-com:device:ScaleSensor:1", "D_ScaleSensor1.xml", "Weight "],
				'S_POWER': [13, "urn:schemas-micasaverde-com:device:PowerMeter:1", "D_PowerMeter1.xml", "Power "],
				'S_HEATER': [14, "urn:schemas-upnp-org:device:Heater:1", "D_Heater1.xml", "Heater "],
				'S_DISTANCE': [15, "urn:schemas-upnp-org:device:Distance:1", "D_DistanceSensor1.xml", "Distance "],
				'S_LIGHT_LEVEL': [16, "urn:schemas-micasaverde-com:device:LightSensor:1", "D_LightSensor1.xml", "Light "],
				'S_ARDUINO_NODE': [17, "urn:schemas-arduino-cc:device:arduinonode:1", "D_ArduinoNode1.xml", "Node "],
				'S_ARDUINO_RELAY': [18, "urn:schemas-arduino-cc:device:arduinorelay:1", "D_ArduinoRelay1.xml", "Relay "],
				'S_LOCK': [19, "urn:micasaverde-com:serviceId:DoorLock1", "D_DoorLock1.xml", "Lock "],
				'S_IR': [20, "urn:schemas-arduino-cc:device:ArduinoIr:1", "D_ArduinoIr1.xml", "IR "],
				'S_WATER': [21, "urn:schemas-micasaverde-com:device:WaterMeter:1", "D_WaterMeter1.xml", "Water "],
				'S_AIR_QUALITY': [22, "urn:schemas-micasaverde-com:device:AirQuality:1", "D_AirQuality1.xml", "Air Quality "], 
				'S_CUSTOM': [23,"urn:schemas-micasaverde-com:device:GenericSensor:1", "D_GenericSensor1.xml", "Generic "], 
				'S_DUST': [24,"urn:schemas-micasaverde-com:device:Dust:1", "D_DustSensor1.xml", "Dust "], 
				'S_SCENE_CONTROLLER': [ 25,"urn:schemas-micasaverde-com:device:SceneController:1", "D_SceneController1.xml", "SceneCtrl "]
		}

		self.tVarTypes = {
				'V_TEMP': [0, "urn:upnp-org:serviceId:TemperatureSensor1", "CurrentTemperature", ""],
				'V_HUM': [1, "urn:micasaverde-com:serviceId:HumiditySensor1", "CurrentLevel", "" ],
				'V_LIGHT': [2, "urn:upnp-org:serviceId:SwitchPower1", "Status", "0" ],
				'V_DIMMER': [3, "urn:upnp-org:serviceId:Dimming1", "LoadLevelStatus", "" ],
				'V_PRESSURE': [4, "urn:upnp-org:serviceId:BarometerSensor1", "CurrentPressure", "" ],
				'V_FORECAST': [5, "urn:upnp-org:serviceId:BarometerSensor1", "Forecast", "" ],
				'V_RAIN': [6, "urn:upnp-org:serviceId:RainSensor1", "CurrentTRain", "" ],
				'V_RAINRATE': [7, "urn:upnp-org:serviceId:RainSensor1", "CurrentRain", "" ],
				'V_WIND': [8, "urn:upnp-org:serviceId:WindSensor1", "AvgSpeed", "" ],
				'V_GUST': [9, "urn:upnp-org:serviceId:WindSensor1", "GustSpeed", "" ],
				'V_DIRECTION': [10, "urn:upnp-org:serviceId:WindSensor1", "Direction", "" ],
				'V_UV': [11, "urn:upnp-org:serviceId:UvSensor1", "CurrentLevel", "" ],
				'V_WEIGHT': [12, "urn:micasaverde-com:serviceId:ScaleSensor1", "Weight", "" ],
				'V_DISTANCE': [13, "urn:micasaverde-com:serviceId:DistanceSensor1", "CurrentDistance", "" ],
				'V_IMPEDANCE': [14, "urn:micasaverde-com:serviceId:ScaleSensor1", "Impedance", "" ],
				'V_ARMED': [15, "urn:micasaverde-com:serviceId:SecuritySensor1", "Armed", "" ],
				'V_TRIPPED': [16, "urn:micasaverde-com:serviceId:SecuritySensor1", "Tripped", "0" ],
				'V_WATT': [17, "urn:micasaverde-com:serviceId:EnergyMetering1", "Watts", "" ],
				'V_KWH': [18, "urn:micasaverde-com:serviceId:EnergyMetering1", "KWH", "0" ],
				'V_SCENE_ON': [19, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneActivated", "" ],
				'V_SCENE_OFF': [20, "urn:micasaverde-com:serviceId:SceneController1", "sl_SceneDeactivated", "" ],
				'V_HEATER': [21, "urn:upnp-org:serviceId:HVAC_UserOperatingMode1", "ModeStatus", "" ],
				'V_HEATER_SW': [22, "urn:upnp-org:serviceId:SwitchPower1", "Status", "" ],
				'V_LIGHT_LEVEL': [23, "urn:micasaverde-com:serviceId:LightSensor1", "CurrentLevel", "" ],
				'V_VAR_1': [24, "urn:upnp-org:serviceId:VContainer1", "Variable1", ""],
				'V_VAR_2': [25, "urn:upnp-org:serviceId:VContainer1", "Variable2", ""],
				'V_VAR_3': [26, "urn:upnp-org:serviceId:VContainer1", "Variable3", ""],
				'V_VAR_4': [27, "urn:upnp-org:serviceId:VContainer1", "Variable4", ""],
				'V_VAR_5': [28, "urn:upnp-org:serviceId:VContainer1", "Variable5", ""],
				'V_UP': [29, None, None, ""],
				'V_DOWN': [30, None, None, ""],
				'V_STOP': [31, None, None, ""],
				'V_IR_SEND': [32, None, None, ""],
				'V_IR_RECEIVE': [33, "urn:upnp-org:serviceId:ArduinoIr1", "IrCode", ""],
				'V_FLOW': [34, "urn:micasaverde-com:serviceId:WaterMetering1", "Flow", "" ],
				'V_VOLUME': [35, "urn:micasaverde-com:serviceId:WaterMetering1", "Volume", "0" ],
				'V_LOCK': [36, "urn:micasaverde-com:serviceId:DoorLock1", "Status", ""],
				'V_DUST_LEVEL': [37, "urn:micasaverde-com:serviceId:DustSensor1", "DustLevel", ""],
				'V_VOLTAGE': [38, "urn:micasaverde-com:serviceId:EnergyMetering1", "Voltage", ""],
				'V_CURRENT': [39, "urn:micasaverde-com:serviceId:EnergyMetering1", "Current", ""]
			}

		self.tInternalTypes = {
				'I_BATTERY_LEVEL': [0, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryLevel", "" ],
				'I_TIME': [1, None, None, None],
				'I_VERSION': [2, "urn:upnp-arduino-cc:serviceId:arduinonode1", "ArduinoLibVersion", ""],
				'I_ID_REQUEST': [3, None, None, None],
				'I_ID_RESPONSE': [4, None, None, None],
				'I_INCLUSION_MODE': [5, "urn:upnp-arduino-cc:serviceId:arduino1", "InclusionMode", "0"],
				'I_CONFIG': [6, "urn:upnp-arduino-cc:serviceId:arduinonode1", "RelayNode", ""],
				'I_PING': [7, None, None, None ],
				'I_PING_ACK': [8, None, None, None ],
				'I_LOG_MESSAGE': [9, None, None, None ],
				'I_CHILDREN': [10, "urn:upnp-arduino-cc:serviceId:arduinonode1", "Children", "0"],
				'I_SKETCH_NAME': [11, "urn:upnp-arduino-cc:serviceId:arduinonode1", "SketchName", ""],
				'I_SKETCH_VERSION': [12, "urn:upnp-arduino-cc:serviceId:arduinonode1", "SketchVersion", ""],
				'I_REBOOT': [13, None, None, None], 
				'I_GATEWAY_READY': [14, None, None, None]
		}

		self.tVeraTypes = {
				'BATTERY_DATE': [0, "urn:micasaverde-com:serviceId:HaDevice1", "BatteryDate", "" ],
				'LAST_TRIP': [1, "urn:micasaverde-com:serviceId:SecuritySensor1", "LastTrip", "" ],
				'LAST_UPDATE': [2, "urn:micasaverde-com:serviceId:HaDevice1", "LastUpdate", "" ]
		}
		
		self.reloadConfig(True)
		
		self.tVarLookupNumType  = {}
		self.tDeviceLookupNumType  = {}
		self.tInternalLookupNumType = {}
		self.tVeraLookupNumType  = {}
		
		for k, v in self.tVarTypes.iteritems():
			self.tVarLookupNumType[v[0]] = k

		for k, v in self.tDeviceTypes.iteritems():
			self.tDeviceLookupNumType[v[0]] = k
	
		for k, v in self.tInternalTypes.iteritems():
			self.tInternalLookupNumType[v[0]] = k
		
		for k, v in self.tVeraTypes.iteritems():
			self.tVeraLookupNumType[v[0]] = k
		
			
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
				
			if messageType==self.msgType['SET']:
				self.setVariable(incomingData, device, nodeId)
			elif messageType==self.msgType['PRESENTATION']:
				self.presentation(incomingData, device, childId, altId)
			elif messageType==self.msgType['REQUEST']:
				self.requestStatus(incomingData, device, altId)
			elif messageType==self.msgType['INTERNAL']:
				self.processInternalMessage(incomingData, device, altId)
			else:
				self.log.error("processIncoming: Error: Classic you shouldn't end up here: "+ s)
		else:
			self.log.error("processIncoming: Error: Receive unknown data: "+ s)
		
	def  presentation(self, incomingData, device, childId, altId):
		type = incomingData[4]
		data = incomingData[5]
		mode = bool(self.InclusionMode)
		print mode
		if (mode is True and device is None):
			#A new sensor (not created before) was presented during inclusion mode
			if (altId not in self.inclusionResult): 
				self.log.info("presentation: New sensor starting up. Radio: "+ incomingData[0] + " Sensor: "+incomingData[1])
				self.includeCount = self.includeCount+1;
				
				print device
				print childId
				print altId
				print type
				
				#Find max current childId add one for the new sensor.
				# not nice but this is how I try to learn python, 5 years from now I will cry over this solution.
				index = -1
				for k, v in self.config.items("childIds") :
					if int(k) > index :
						index = int(k)
				
				index += 1
				
				print index
				
				self.childIdLookupTable[altId] = index
				self.config.set('childIds',str(index),altId+";"+type)
				
				self.writeConfigFile()
				
				self.inclusionResult[altId] = type
			elif (mode == 0 and device is not None and childId == self.NODE_CHILD_ID and data != self.GATEWAY_VERSION):
				#The library version of sensor differs from plugin version. Warn about it.
				self.log.warn("presentation: Doesn't match Gateway version("+self.GATEWAY_VERSION+ "). Radio: "+ incomingData[0] + " Sensor: "+incomingData[1] + " using version: " + incomingData[4])

	def processInternalMessage(self, incomingData, iChildId, iAltId):
		data = incomingData[5]
		index = int(incomingData[4]);
		varType = self.tInternalLookupNumType[index]
		var = self.tInternalTypes[varType]
		print incomingData
		print var
		print varType
		if (varType == "I_VERSION" and iAltId == "0;0"):
			#Store version of Arduino Gateway
			self.GATEWAY_VERSION = data
			self.log.info('processInternalMessage: Gateway running version: '+self.GATEWAY_VERSION )
			print("Connected to Mysensor Gateway running version %s" % data)
		elif ((varType == "I_SKETCH_NAME" or varType == "I_SKETCH_VERSION") and iChildId is not None) :
			# Store the Sketch name and Version
			v = self.config.get('childIds',str(iChildId))
			d = v.split(";")
			name = d[2]
			version = d[2]
			if varType == "V_SKETCH_NAME" : 
				name = data.rstrip()
			elif varType == "V_SKETCH_VERSION" :
				version = data.rstrip()
			
			self.config.set('childIds',str(iChildId),iAltId+";"+name+";"+version)
			
			self.writeConfigFile()

		elif (varType == "I_TIME"):
			#Request time was sent from one of the sensors
			self.sendInternalCommand(iAltId,"I_TIME",time.time())
		elif (varType == "I_CONFIG"):
			#Request for unit was sent from one of the sensors
			self.sendInternalCommand(iAltId,"I_CONFIG",self.unit)
		elif (varType == "I_ID_REQUEST"):
			#Determine next available radioid and sent it to the sensor
			self.sendInternalCommand(iAltId,"I_ID_RESPONSE",self.nextAvailiableRadioId())
		elif (varType == "I_RELAY_NODE" and iChildId is not None):
			#Set human readable relay mode status
			self.setVariableIfChanged(var[1], var[2], data, iChildId)
			### Have a look at the one below
			#setVariableIfChanged(var[1], "RelayNodeHR", data == "0" and "GW" or data, iChildId)
		elif (varType == "I_BATTERY_LEVEL"):
		# Send to serVariable since you usally want to store this info.
			self.setVariable(incomingData, str(iChildId), iAltId)			
		elif (varType == "I_INCLUSION_MODE"):
			if data == "0" : 
				self.log.info("processInternalMessage: Inclusion mode started")
			elif data == "1" :
				self.log.info("processInternalMessage: Inclusion mode ended")
		elif (varType == "I_CHILDREN"):
			self.setVariableIfChanged(var[1], var[2], data, iChildId)
		elif (varType == "I_LOG_MESSAGE" or varType == "I_GATEWAY_READY"):
			self.log.info("processInternalMessage: Log message:" + data)
		else:
			self.log.info("processInternalMessage: Incoming internal command discarded:" + data)	

	def nextAvailiableRadioId(self):
		for i in xrange(10,254): 
			if (self.availableIds[i] == True):
				self.availableIds[i] = False
				return i
		return 255

	def setVariable(self, incomingData, childId, nodeId):
		if (childId is not None) :
			# Set variable reported from a child sensor.
			base_topic = self.config.get('config','mqtt_topic')
			childId = str(childId)
			index = int(incomingData[4]);
			varType = self.tVarLookupNumType[index]
			var = self.tVarTypes[varType]
			sensorId = incomingData[1]
			value = incomingData[5].rstrip()
			device = self.childIdLookupTable[incomingData[0]+";255"] 
			if (self.config.getboolean('config','mqtt_sketchinfo') ):
				v = self.config.get('childIds',str(device))
				d = v.split(";")
				name = d[2]
			else:
				name = incomingData[0]
			
			if (var[1] is not None): 
				self.log.info("setVariable: RaidoId: "+incomingData[0]+" Sensor: "+incomingData[1]+" ChildId: "+str(childId)+" Type: " +self.tVarLookupNumType[index]+" reporting value: "+ value)
				topic = base_topic+'from/'+name+'/'+sensorId
				self.client.publish(topic,value)
				print "pub:"+topic+" "+value
				self.last_topic = topic
				self.last_message = value
				self.setVariableIfChanged(var[1], var[2], value, childId)


	# Still here since a lot of methods sends info to this one.
	def setVariableIfChanged(self, serviceId, name, value, deviceId):
		self.log.info("setVariableIfChanged: "+serviceId +","+name+", "+str(value)+", "+str(deviceId))	
	
	def processMqttMessage(self,msg):
		topic = msg.topic
		value = msg.payload
		base_topic = self.config.get('config','mqtt_topic')
		print 'test '+topic
		print topic.startswith(base_topic+'to/')
		if (topic.startswith(base_topic+'to/')): 
			print "qwerty"
			# local commands
			if (topic == base_topic+"to/cmd"):
				if value == "reloadconfig" :
					self.reloadConfig()
			
			else :
			#Mysernsor commands
				t = topic.split('/')
				node = t[-3]
				type = t[-1]
				altid = t[-3]+';'+t[-2]
				#childId = self.childIdLookupTable[altid]
				print "bra"
				self.sendCommand(altid,type,value)
				print "bra2"
			
	# Function to send a message to sensor
	def sendCommand(self, altid, variableId, value):
		print altid
		print variableId
		print value
		return self.sendCommandWithMessageType(altid, "SET", 1, int(self.tVarTypes[variableId][0]), value)

	def sendNodeCommand(self, device, variableId, value):
		return self.sendCommandWithMessageType(device+";255", "SET",1, int(self.tVarTypes[variableId][0]), value)

	def sendInternalCommand(self, altid, variableId, value):
		return self.sendCommandWithMessageType(altid, "INTERNAL", 0, int(self.tInternalTypes[variableId][0]), str(value))

	def sendRequestResponse(self, altid, variableId, value):
		return self.sendCommandWithMessageType(altid, "SET", 0, int(self.tVarTypes[variableId][0]), value)
		
	def sendCommandWithMessageType(self, altid, messageType, ack, variableId, value):
		cmd = altid+";"+self.msgType[messageType]+";"+str(ack)+";"+str(variableId)+";"+value+"\n"
		print cmd
		#serial keep if I want to enable it again... later todo
		if self.ser.writable:
 			self.ser.write(cmd)
			self.log.debug("sendCommandWithMessageType: Sending: "+cmd)
			return True
		else:
			self.log.error("sendCommandWithMessageType: Can't write to serial port")
			return False
	
	def loop(self):
		response = self.ser.readline()
		if response:
			self.log.debug("loop: Incomming message: "+response)
			self.processIncoming(response)
			return response
		return None	
	
	#Arduino GW device commands
	def startInclusion(self):
		self.config.set('config','inclusion-mode',"true")
		return self.sendInternalCommand("0;0","I_INCLUSION_MODE","1")


	def stopInclusion(self):
		self.config.set('config','inclusion-mode',"false")
		return self.sendInternalCommand("0;0","I_INCLUSION_MODE","0")
		
		### Support functions 	
	def reloadConfig(self, bootup = False) :
		#load known sensors from file
		for k, v in self.config.items("childIds") :
			value = v.split(';')
			self.childIdLookupTable[value[0]+";"+value[1]] = k
			self.availableIds[int(value[0])]=False
		
		#load unit M/I from file (A good programmer should check input values)
		self.unit = self.config.get('config','unit')
		
		#load InclutionMode from file and send it to gateway(A good programmer should check input values...)
		self.InclusionMode = self.config.getboolean('config','inclusion_mode')
		
		#self.mysensor_ip = self.config.get('config','mysensor_ip')
		#self.mysensor_port = self.config.get('config','mysensor_port')
		
		#at bootup this is executed from init
		if bootup is False :
			self.setInclusionMode(self.InclusionMode)
	
		self.log.info("reloadConfig: Configuration reloaded.")
		
		
	#Parse Inclusion mode and sends the command to the Gateway
	def setInclusionMode(self, value) :
		if value is True :
			self.startInclusion()
		elif value is False :
			self.stopInclusion()
		else :
			self.log.warn("setInclutionMode : Invalid value :" +str(value))
		self.writeConfigFile()

	# Write persist the config file
	def writeConfigFile(self) :
		with open('mspmqtt.conf', 'wb') as configfile:
			self.config.write(configfile)
