/*
	Arduino code for Triggering the Photon Camera from serial interface.
	AUTHOR: 乔昂
	DATE: 26/10/2022
*/

#include <Arduino.h>

void setup()
{
	pinMode(8, OUTPUT);
	digitalWrite(8, LOW);
	Serial.begin(9600); 
}

void loop()
{
	if (Serial.available() > 0)
	{
		if(Serial.read() == 49){
			digitalWrite(8, HIGH);
			delay(1);
			digitalWrite(8, LOW);
			delay(50);
			digitalWrite(8, HIGH);
			delay(1);
			digitalWrite(8, LOW);
		}
		Serial.print("Start Reccording!");
	}

}
