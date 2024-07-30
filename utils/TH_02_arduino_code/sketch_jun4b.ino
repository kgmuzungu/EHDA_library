#include <TH02_dev.h>
#include "Arduino.h"
#include "Wire.h"
#include "THSensor_base.h"

#ifdef __AVR__
    #include <SoftwareSerial.h>
    SoftwareSerial SSerial(2, 3); // RX, TX
    #define COMSerial Serial
    #define ShowSerial Serial
    TH02_dev TH02;
#endif

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
    #define COMSerial Serial1
    #define ShowSerial SerialUSB
    TH02_dev TH02;
#endif

#ifdef ARDUINO_ARCH_STM32F4
    #define COMSerial Serial
    #define ShowSerial SerialUSB
    TH02_dev TH02;
#endif

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  /* Power up,delay 150ms,until voltage is stable */
  delay(150);
  /* Reset HP20x_dev */
  TH02.begin();
  delay(100);
}

void loop() {
  // put your main code here, to run repeatedly:
  float temper = TH02.ReadTemperature();
  float humidity = TH02.ReadHumidity();

  String temp_message = String("temp") + "-" + String(temper);
  String humidity_message = String("humy") + "-" + String(humidity);

  Serial.println(temp_message);
  Serial.println(humidity_message);

  delay(1000);
}
