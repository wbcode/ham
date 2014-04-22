import logging
import ConfigParser
import rrdtool

class Rrd():

	def setVariable(self, incomingData, childId, nodeId):
	# should cache this data but not now.
		value = incomingData[4]
		if self.config.has_option('rrds',childId) :
			rrds = self.config.get('rrds',childId)
			arrds = rrds.split(",")
			for s in arrds:
				splitted = s.split(";")
				file = splitted[0]
				ds = splitted[1]
				ret = rrdtool.update('rrd/'+file+'.rrd', '-t',ds, 'N:'+value.strip())
				self.log.debug('setVariable Rrd update command: rrd/'+file+'.rrd -t '+ ds + ' N:'+value.strip())
				if ret:
					self.log.error('setVariable: RRD :'+rrdtool.error())
		
	#Implement
	def requestStatus(self, incomingData, childId, altId):
		return None
		
	#Implement
	def parseCommand(self,type,state) :
		return None
	
	#Implement
	def reloadConfig(self) :
		return None
	
	def __init__(self, xconfig, xlog):
		self.log=xlog
		self.config=xconfig
		
