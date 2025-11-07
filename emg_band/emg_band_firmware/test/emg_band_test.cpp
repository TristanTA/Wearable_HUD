// emg_band_test.cpp
// Works on Seeed Studio XIAO ESP32-S3
// BLE version for testing EMG signals over Bluetooth

#include <Arduino.h>
#include <NimBLEDevice.h>

#define NUM_EMG_CHANNELS 3
int sensorPins[NUM_EMG_CHANNELS] = {A0, A1, A2};

NimBLEServer *pServer;
NimBLECharacteristic *pCharacteristic;
bool deviceConnected = false;

// UUIDs for your BLE service and characteristic
#define SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

class ServerCallbacks : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer* pServer) {
        deviceConnected = true;
    }
    void onConnect(NimBLEServer* pServer, ble_gap_conn_desc* desc) {
        deviceConnected = true;
    }
    void onDisconnect(NimBLEServer* pServer) {
        deviceConnected = false;
    }
};



void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) pinMode(sensorPins[i], INPUT);

  Serial.println("=== EMG BAND TEST (BLE) ===");
  Serial.println("Advertising as EMG_Band_Test (BLE UART)");
  
  NimBLEDevice::init("EMG_Band_Test");
  pServer = NimBLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());
  NimBLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
      CHARACTERISTIC_UUID,
      NIMBLE_PROPERTY::NOTIFY
  );

  pService->start();
  pServer->getAdvertising()->start();

  Serial.println("BLE service started. Connect via nRF Connect, Serial Bluetooth Terminal, etc.");
}

void loop() {
  int values[NUM_EMG_CHANNELS];
  for (int i = 0; i < NUM_EMG_CHANNELS; i++)
    values[i] = analogRead(sensorPins[i]);

  char msg[32];
  sprintf(msg, "%d,%d,%d\n", values[0], values[1], values[2]);

  Serial.print(msg);
  if (deviceConnected) pCharacteristic->setValue((uint8_t*)msg, strlen(msg)), pCharacteristic->notify();

  // Blink LED heartbeat
  static unsigned long lastBlink = 0;
  if (millis() - lastBlink > 500) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    lastBlink = millis();
  }

  delay(5); // ~200 Hz sample rate
}
