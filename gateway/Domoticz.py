import json
import requests
import logging
import ConfigParser

class Domoticz():

	def setVariable(self, incomingData, childId, nodeId):
	# should cache this data but not now.
		value = incomingData[4]
		domoticzs = self.config.get('domoticz',childId)
		adomoticzs = domoticzs.split(";")
		#http://domoticz-ip/json.htm?type=devices&used=all
		#type=command&param=udevice&idx=10&nvalue=0&svalue=12.3
		data = {'type':'command','param':'udevice','idx':str(adomoticzs[0]),str(adomoticzs[1]):str(value.strip())}
					
		url = self.config.get('config','domoticz_url')

		resp = requests.get(url=url, params=data)
		self.log.debug("setVariable: Domoticz get url: "+resp.url )
					
		if resp.status_code != 200 :
			self.log.error("setVariable: Domoticz get url: "+resp.url+" Response code:" + resp.status_code )
		data = json.loads(resp.content)
		if data['status'] != 'OK' :
			self.log.error("setVariable: Domoticz get url: "+resp.url+" Domoticz error:" + data )

		#Implement
		def requestStatus(self, incomingData, childId, altId):
			return None
			
		#Implement
		def parseCommand(self,type,state) :
			return None
	
	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig
			