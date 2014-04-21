import json
import requests
import logging
import ConfigParser
import colorsys

class Openhab():
	
	openhabNameTypeLookup = {}
	openHabLookupTable = {}
	
	def setVariable(self, incomingData, childId, nodeId):
		value = str(incomingData[4].strip())
		item = self.config.get('openhab',childId)
		data = None
		
		headers = {'Content-Type': 'text/plain', 'Accept' : 'application/json'}
		
		url = self.config.get('config','openhab_url')
		url+=item+'/state'
		
		#find openhab type
		openhabtype = self.openhabNameTypeLookup[item]
		
		#convert input value to fit Openhab
		if openhabtype == "NumberItem" :
			data = value
		elif openhabtype == "ContactItem" :
			if value == "0" :
				data = "CLOSED"
			elif value == "1" :
				data = "OPEN"
			else : 
				data = None
		elif openhabtype == "StringItem" :
			data = value
		else:
			data = None
			self.log.error("setVariable: Can't find openhab item type. Openhab item name: "+ item)
		
		# send data to openhab
		if data is not None :
			#add "verify=False" to not verify SSL certificates.
			resp = requests.put(url=url, data=data, headers=headers)
			self.log.debug("setVariable: Openhab put url: "+resp.url+" Data: "+ data )
			if resp.status_code != 200 :
				self.log.error("setVariable: Openhab put url: "+resp.url+" Response code:" + str(resp.status_code) )
		else :
			self.log.error("setVariable: Can't parse incomming value: "+ value)
					
	def requestStatus(self, incomingData, childId, altId):
		item = self.config.get('openhab',childId)
		headers = {'Accept' : 'application/json'}
		
		url = self.config.get('config','openhab_url')
		url+=item
		
		resp = requests.get(url=url, headers=headers)
		if resp.status_code != 200 :
			self.log.error("requestStatus: Openhab get url: "+resp.url+" Response code:" + str(resp.status_code) )
		data = json.loads(resp.content)
		print resp.content
		if data['type'] == 'SwitchItem' :
			if data['state'] == 'OFF' :
				self.log.debug("requestStatus: Openhab get url: "+resp.url+" Openhab state:" + str(data) )
				return "0"
			elif data['state'] == 'ON' :
				self.log.debug("requestStatus: Openhab get url: "+resp.url+" Openhab state:" + str(data) )
				return "1"
			else :
				self.log.error("requestStatus: Openhab get url: "+resp.url+" Openhab error:" + str(data) )
				return None
		
		else :
			self.log.error("requestStatus: Openhab unsupported type: get url: "+resp.url+" Openhab error:" + str(data) )
			return None
		
	def parseCommand(self,type,state) :
		if type == 'SwitchItem' :
			if state == "ON" :
				return "2;1"
			elif state == "OFF" or state == "Uninitialized" :
				return "2;0"
			else :
				return None
		elif type == 'ColorItem' :
			#Convert value from HSL to RGB
			hsv = state.split(',')
			rgb = colorsys.hsv_to_rgb(float(hsv[0])/360,float(hsv[1])/100,float(hsv[2])/100)
			hex = "%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
			print rgb
			print hex
			return "32;0x"+hex
		else :
			return None
	
	#Get itemes that exist in Openhab
	def getOpebHabItems(self) :
		
		self.openhabNameTypeLookup = {}
		
		headers = {'Accept' : 'application/json'}
		url = self.config.get('config','openhab_url')
		url+="?type=json"
		resp = requests.get(url=url, headers=headers)
		if resp.status_code != 200 :
			self.log.error("getOpebHabItems: Openhab get url: "+resp.url+" Response code:" + str(resp.status_code) )
		
		data = json.loads(resp.content)
		
		#populate openhab info
		for v in data["item"] :
			self.openhabNameTypeLookup[v["name"]] = v["type"]
	
	def getChildIdFromNane(self, name) :
		if name in self.openHabLookupTable :
			return self.openHabLookupTable[name]
		else :
			return None
	
	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig
		
		self.getOpebHabItems()
		
		#populate openHabLookupTable
		for k, v in self.config.items("openhab") :
			self.openHabLookupTable[v] = k