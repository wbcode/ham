### This is not finished
* just commied it so others can have a try. It's full of errors and debug output

### Short overview
* Automaticly assigns Raido ID:s
* Support bidirectional integration using mqtt
* Runs on Raspberry Pi with a Arduino Uno connected with USB
* You must have a mqtt broker installed. i.e www.mosquitto.org
* Support MySensors protocol 1.4


### Testing
* Tested using a Arduino Uno as Mysensor Gateway
* Relay and humidity sensor

### TODO
* sort out threading
* present mqtt configuration/topic on the webserver (preferably openhab configuration)
* testing more sensors
* Clean up a lot of code and poor mans debug output (i.e print)

### run
configure "mspmqtt.conf"

and run using "python mspmqtt.py"

### MQTT - topic
```
mysensors/<to|from>/<radio_id>/<sensor_id>/<type>
```
ie. 
```
mysensors/to/11/1/V_LIGHT
```
base name "mysensors" is configurable in the config file.

### Configuration in Openhab 

## site.item-file
```
Number Temperature_FV_MQTT	"MQTT Temperature [%.1f °C]"	<temperature>	(Temperature, FV_Mancave) { mqtt="<[pi:mysensors/from/10/1:state:default]" }
Number Humidity_FV_MQTT		"MQTT Humidity [%d %%]" 		<waterdrop> 	(Humidity, FV_Mancave)	{ mqtt="<[pi:mysensors/from/10/0:state:default]" }

Switch Relay1_FV_Mancave 	"Relay 1" 	<light> 	(Relays, FV_Mancave) {mqtt=">[pi:mysensors/to/11/1/V_LIGHT:command:*:MAP(switchFromMqtt.map)]"}
Switch Relay2_FV_Mancave 	"Relay 2" 	<light> 	(Relays, FV_Mancave) {mqtt=">[pi:mysensors/to/11/2/V_LIGHT:command:*:MAP(switchFromMqtt.map)]"}

Switch Gateway_reload_config "Reload Gateway config" {mqtt=">[pi:mysensors/to/cmd:command:*:reloadconfig)]"}
```
## transformation/switchFromMqtt.map
```
OFF=0
ON=1
1=ON
0=OFF
```
## site.rules
```
/*Send a reload request to the gateway */
rule "Reload Gateway Config" 
when
	Item Gateway_reload_config changed 
then
	if (Gateway_reload_config.state == ON) {
		Thread::sleep(5000) 
		Gateway_reload_config.state = OFF
		}

end
``` 