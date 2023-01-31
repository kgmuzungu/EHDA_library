/*
	Arduino code for Triggering the Photon Camera from serial interface.
	AUTHOR: 乔昂
	DATE: 26/10/2022
*/

#include <Arduino.h>
#include "DHT.h"
#define DHTPIN 8
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup()
{
	Serial.begin(9600);
	dht.begin();
}

void loop()
{

	float h = dht.readHumidity();
	float t = dht.readTemperature();
	Serial.print("humy-");
	Serial.print(h);
	Serial.println();
	Serial.print("temp-");
	Serial.print(t);
	Serial.println();
	delay(500);

	
}
