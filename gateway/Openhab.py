import json
import requests
import logging
import ConfigParser

class Openhab():

	def setVariable(self, incomingData, childId, nodeId):
		value = incomingData[4]			
		item = self.config.get('openhab',childId)
		data = str(value.strip())
		headers = {'Content-Type': 'text/plain', 'Accept' : 'application/json'}
		
		url = self.config.get('config','openhab_url')
		url+=item+'/state'
		
		
		#add "verify=False" to not verify SSL certificates.
		resp = requests.put(url=url, data=data, headers=headers)
		self.log.debug("setVariable: Openhab put url: "+resp.url+" Data: "+ data )
		if resp.status_code != 200 :
			self.log.error("setVariable: Openhab put url: "+resp.url+" Response code:" + resp.status_code )
	
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
		else :
			return None
	
	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig