#include <Arduino.h>
#include <BluetoothSerial.h>

// Bluetooth Object
BluetoothSerial SerialBT;

// Global Variables
#define NUM_EMG_CHANNELS 3
int sensorPins[NUM_EMG_CHANNELS] = {A0, A1, A2};
int sensorValues[NUM_EMG_CHANNELS];
bool isBluetoothConnected = false;

// Init Function Declarations
void checkPowerStatus();
void handleBluetoothConnection();
void handleFileUpload();
void readAndSendSensorData();

//Upon start do:
void setup() {
  // Starts US serial communication with computer
  Serial.begin(115200);
  Serial.println("EMG Band Booting...");

  // Turn on Indicator LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  // Set Analog pins as Inputs
  for (int i = 0; i < NUM_EMG_CHANNELS; i++)
    pinMode(sensorPins[i], INPUT);

  //Init Bluetooth
  SerialBT.begin("EMG_Band_V0"); // Name displayed for Bluetooth
  Serial.println("Bluetooth started.Waiting for connection...");
}

void loop() {
  checkPowerStatus();
  handleBluetoothConnection();
  handleFileUpload();
  readAndSendSensorData();
}

// Functions
void checkPowerStatus() {
  //TODO: detect USB or battery state
}

void handleBluetoothConnection() {
  isBluetoothConnected = SerialBT.hasClient();
}

void handleFileUpload() {
  if (Serial.available())
    Serial.println("USB data incoming...");
  if (SerialBT.available())
    Serial.println("BT data incoming...");
}

void readAndSendSensorData(){
  // If Bluetooth is not connected, exit
  if (!isBluetoothConnected) return;
  // Read voltage from channels
  for (int i = 0; i < NUM_EMG_CHANNELS; i++)
    sensorValues[i] = analogRead(sensorPins[i]);\
  // Append sensor values to packet
  String packet;
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) {
    packet += String(sensorValues[i]);
    if (i < NUM_EMG_CHANNELS - 1) packet += ",";
  // Sends packet over Bluetooth
  SerialBT.println(packet);
  delay(10); // Pause for 10 ms
  }
}