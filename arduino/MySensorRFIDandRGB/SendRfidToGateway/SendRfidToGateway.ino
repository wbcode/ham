/*
 * MFRC522 - Library to use ARDUINO RFID MODULE KIT 13.56 MHZ WITH TAGS SPI W AND R BY COOQROBOT.
 * The library file MFRC522.h has a wealth of useful info. Please read it.
 * The functions are documented in MFRC522.cpp.
 *
 * Based on code Dr.Leong   ( WWW.B2CQSHOP.COM )
 * Created by Miguel Balboa (circuitito.com), Jan, 2012.
 * Rewritten by Søren Thing Andersen (access.thing.dk), fall of 2013 (Translation to English, refactored, comments, anti collision, cascade levels.)
 * Released into the public domain.
 *
 * Sample program showing how to read data from a PICC using a MFRC522 reader on the Arduino SPI interface.
 *----------------------------------------------------------------------------- empty_skull 
 * Aggiunti pin per arduino Mega
 * add pin configuration for arduino mega
 * http://mac86project.altervista.org/
 ----------------------------------------------------------------------------- Nicola Coppola
 * Pin layout should be as follows:
 * Signal     Pin              Pin               Pin
 *            Arduino Uno      Arduino Mega      MFRC522 board
 * ------------------------------------------------------------
 * Reset      9                5                 RST
 * SPI SS     10               53                SDA
 * SPI MOSI   11               52                MOSI
 * SPI MISO   12               51                MISO
 * SPI SCK    13               50                SCK
 *
 * The reader can be found on eBay for around 5 dollars. Search for "mf-rc522" on ebay.com. 
 */

#include <Sleep_n0m1.h>
#include <SPI.h>
#include <MFRC522.h>
#include <EEPROM.h>  
#include <RF24.h>
#include <Sensor.h> 

//MySensor define
#define CHILD_ID 0   // Id of the sensor child fix this

//RFID define
#define SS_PIN 6
#define RST_PIN 5


MFRC522 mfrc522(SS_PIN, RST_PIN);	// Create MFRC522 instance.
Sensor gw;
Sleep sleep;


void setup() {
        
        EEPROM.write(EEPROM_RELAY_ID_ADDRESS, 0);
  
        gw.begin();
      
        // Send the sketch version information to the gateway and Controller
        gw.sendSketchInfo("RFID", "1.0");
      
        // Using S_IR for testing purpuse, IR is hex encoded so are the RFID uid:s
        gw.sendSensorPresentation(CHILD_ID, S_IR);
        
	Serial.begin(115200);	// Initialize serial communications with the PC
	SPI.begin();			// Init SPI bus
	mfrc522.PCD_Init();	// Init MFRC522 card
	Serial.println("Scan PICC to see UID and type...");
}

void loop() {
	// Look for new cards
	if ( ! mfrc522.PICC_IsNewCardPresent()) {
		return;
	}

	// Select one of the cards
	if ( ! mfrc522.PICC_ReadCardSerial()) {
		return;
	}

	// Dump debug info about the card. PICC_HaltA() is automatically called.
	//mfrc522.PICC_DumpToSerial(&(mfrc522.uid));
        Serial.print("Card UID:");
	for (byte i = 0; i < mfrc522.uid.size; i++) {
		Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : "");
		Serial.print(mfrc522.uid.uidByte[i], HEX);
               
	}
        Serial.println();
        //Serial.print("UID : ");
        //Serial.println(String(mfrc522.uid.uidByte));
        
        mfrc522.PICC_HaltA();
                
        char carray[mfrc522.uid.size*2];
        uidToCharArray(mfrc522.uid.uidByte,carray);
        Serial.print("\nTest: ");
        Serial.print(carray);
        
        gw.sendVariable(CHILD_ID, V_IR_RECEIVE, carray);  // Send UID to gw 
 
        // Power down the radio.  Note that the radio will get powered back up
        // on the next write() call.
        delay(200); //delay to allow serial to fully print before sleep
        gw.powerDown();
        sleep.pwrDownMode(); //set sleep mode
        //sleep.sleepInterrupt(INTERRUPT,CHANGE); Should check this out and ocnnect IRQ between arduino and RFID reader.
        
}



void uidToCharArray(byte uid[],char carr[]) {
    int j = 0;
    //Serial.print("Here are the bytes: ");
    for (int i = 0; i < 4; i++) {
        byte hinibble = (uid[i] >> 4) & 0x0f;
        byte lonibble = uid[i] & 0x0f;
        //Serial.print(hinibble, HEX);
        //Serial.print(lonibble, HEX);
        //Serial.print(' ');
        carr[j++] = binToHexAscii(hinibble);
        carr[j++] = binToHexAscii(lonibble);
    }
    carr[j] = '\0';    
    
  //  Serial.print("\nHere is the string: ");
  //  Serial.println(carr);
  //  Serial.println();
  //  delay(1000);
}

char binToHexAscii(byte x)
{
    char hex[16] = {
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'
    };
    return hex[x & 0x0f];
}
