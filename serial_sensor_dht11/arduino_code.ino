#include "DHT.h"

#define DHTPIN A1 // pino que estamos conectado
#define DHTTYPE DHT11 // DHT 11

// Conecte pino 1 do sensor (esquerda) ao +5V
// Conecte pino 2 do sensor ao pino de dados definido em seu Arduino
// Conecte pino 4 do sensor ao GND
// Conecte o resistor de 10K entre pin 2 (dados)
// e ao pino 1 (VCC) do sensor
DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  Serial.begin(9600);
  Serial.println("DHTxx test!");
  dht.begin();
}

void loop()
{
  // A leitura da temperatura e umidade pode levar 250ms!
  // O atraso do sensor pode chegar a 2 segundos.
  float h = dht.readHumidity();
  float t = dht.readTemperature();


  if (isnan(t) || isnan(h))
  {
    Serial.println("Failed to read from DHT");

  }
  else
  {
    // Serial.print("Humidity:");
    Serial.print(h);
    Serial.print("x");
    // Serial.print("Temperatura: ");

    Serial.print(t);
    // Serial.println(" *C");
  }
}