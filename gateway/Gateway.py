#! /usr/bin/python2.7
import os
import json
import tornado.ioloop
import tornado.web
import serial
from VeraGW import *
import ConfigParser

#read config file
config = ConfigParser.ConfigParser()
config.read("VeraGW.conf")

# Setup logging
log = logging.getLogger('VeraGW')
hdlr = logging.FileHandler(config.get('config','log_file'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

# Create VeraGW 
vera = VeraGW(config,log)

tornadoPort = int(config.get('httpd','port'))
cwd = os.getcwd() # used by static file server
serialHistory = ''
mostRecentLine = ''

def checkVera():
	line = vera.loop()
	if line is not None :
		global serialHistory
		global mostRecentLine
		mostRecentLine = line
		serialHistory += line

# send the index file
class IndexHandler(tornado.web.RequestHandler):
    def get(self, url = '/'):
        self.render('index.html')
    def post(self, url ='/'):
        self.render('index.html')


# handle commands sent from the web browser
class CommandHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://10.10.11.126")
    #both GET and POST requests have the same responses
    def get(self, url = '/'):
        print "get"
        self.handleRequest()
        
    def post(self, url = '/'):
        print 'post'
        self.handleRequest()
    
    # handle both GET and POST requests with the same function
    def handleRequest( self ):
        # is op to decide what kind of command is being sent
        #op = self.get_argument('op',None)
        
        #received a "checkup" operation command from the browser:
        if self.get_argument('op',None) == "checkup":
            #make a dictionary
            status = {"server": True, "mostRecentSerial": mostRecentLine, "serialHistory": serialHistory}
            #turn it to JSON and send it to the browser
            self.write( json.dumps(status) )
        elif self.get_argument('cmd',None) is not None:
        	  vera.sendCommandOne(self.get_argument('cmd',None))
        	  status = {"server": True, "mostRecentSerial": mostRecentLine, "serialHistory": serialHistory}
        	  self.write( json.dumps(status) )
        #operation was not one of the ones that we know how to handle
        else:
            print op
            print self.request
            raise tornado.web.HTTPError(404, "Missing argument 'op' or not recognized")


# adds event handlers for commands and file requests
application = tornado.web.Application([
    #all commands are sent to http://*:port/com
    #each command is differentiated by the "op" (operation) JSON parameter
    (r"/(com.*)", CommandHandler ),
    (r"/", IndexHandler),
    (r"/(index\.html)", tornado.web.StaticFileHandler,{"path": cwd}),
    (r"/(.*\.png)", tornado.web.StaticFileHandler,{"path": cwd }),
    (r"/(.*\.jpg)", tornado.web.StaticFileHandler,{"path": cwd }),
    (r"/(.*\.js)", tornado.web.StaticFileHandler,{"path": cwd }),
    (r"/(.*\.css)", tornado.web.StaticFileHandler,{"path": cwd }),
])


if __name__ == "__main__":
    
    #tell tornado to run checkVera every 10ms
    serial_loop = tornado.ioloop.PeriodicCallback(checkVera, 10)
    serial_loop.start()
    
    #start tornado
    application.listen(int(config.get('httpd','port')),config.get('httpd','ip'))
    print("Starting server on port number %i..." % tornadoPort )
    print("Open at http://127.0.0.1:%i/index.html" % tornadoPort )
    tornado.ioloop.IOLoop.instance().start()
