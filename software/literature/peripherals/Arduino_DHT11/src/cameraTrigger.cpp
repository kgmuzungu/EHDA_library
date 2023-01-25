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
	if (Serial.available() > 0)
	{
		int value = Serial.readString().toInt();
		if (value == 1)
		{
			float h = dht.readHumidity();
			float t = dht.readTemperature();
			Serial.print("Humidity: ");
			Serial.print(h);
			Serial.print(" %\t");
			Serial.print("Temperature: ");
			Serial.print(t);
			Serial.println(" *C");
		}
		else
		{
			Serial.print("Arduino Wrong Value Received: ");
			Serial.print(value);
		}
	}
}
