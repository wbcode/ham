Start here https://github.com/wbcode/ham/wiki

### Short overview
* Automaticly assigns Raido ID:s
* Support bidirectional integaration with Openhab
* Support unidirectional integaration with Domoticz
* Support storing values in rrd files. You have to create your own rrd files.
* Runs on Raspberry Pi

### Testing
* Tested using a Arduino Uno as Mysensor Gateway

### TODO
* Still needs cleaning from lua code.
* Make it easier to configure.
* Make it module based 
* Replace Configparser to something that don't kill comments in config file.
* Documentation
* Name the python gateway to something 1337 c001...

### Folders
* arduino - lab code that work with MySensor network
* gateway - middleware that integrates MySensor network with third part like Openhab
* www - lab code that can make calls to and from the gateway