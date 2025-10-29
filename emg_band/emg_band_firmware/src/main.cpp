#include <Arduino.h>
#include <BluetoothSerial.h>
#include "FS.h"
#include "SPIFFS.h"
#include <TensorFlowLite.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

extern tflite::MicroInterpreter* interpreter;
extern TfLiteTensor* inputTensor;
extern TfLiteTensor* outputTensor;

// Bluetooth Object
BluetoothSerial SerialBT;

// Global Variables
#define NUM_EMG_CHANNELS 3
int sensorPins[NUM_EMG_CHANNELS] = {A0, A1, A2};
int sensorValues[NUM_EMG_CHANNELS];
bool isBluetoothConnected = false;
const char* MODEL_DIR = "/models/";

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

  if (!SPIFFS.begin(true)) {
  Serial.println("SPIFFS mount failed!");
  return;
    }

  Serial.println("✅ Ready for model upload via USB or Bluetooth.");
}

void loop() {
  checkPowerStatus();
  handleBluetoothConnection();
  handleFileUpload();
  readAndSendSensorData();
}

// Functions
#define USB_SENSE_PIN 4
#define BATTERY_SENSE_PIN A3

bool isUSBConnected = false;
float batteryVoltage = 0.0;

void checkPowerStatus() {
  int usbState = digitalRead(USB_SENSE_PIN);
  int raw = analogRead(BATTERY_SENSE_PIN);
  batteryVoltage = (raw / 4095.0) * 3.3 * 2;

  // Detect USB
  if (usbState == HIGH && !isUSBConnected) {
    Serial.println("USB plugged in — charging mode.");
    isUSBConnected = true;
  } else if (usbState == LOW && isUSBConnected) {
    Serial.println("USB unplugged — switching to battery mode.");
    isUSBConnected = false;
  }

  // Periodically report battery voltage
  static unsigned long lastReport = 0;
  if (millis() - lastReport > 5000) {
    Serial.print("Battery: ");
    Serial.print(batteryVoltage);
    Serial.println(" V");
    lastReport = millis();
  }
}

void handleBluetoothConnection() {
  isBluetoothConnected = SerialBT.hasClient();
}

void handleFileUpload() {
  if (Serial.available()) {
    receiveModelFile(Serial, "usb_model.bin");
  }

  if (SerialBT.available()) {
    receiveModelFile(SerialBT, "bt_model.bin");
  }
}

// --- Receive & save model file ---
void receiveModelFile(Stream &input, const char *defaultName) {
  // Wait for a small header (file name and size)
  if (input.available() < 8) return;  // wait until header starts arriving

  // Read header (format: filename_length, filename, filesize)
  uint8_t nameLen = input.read();
  char filename[64];
  input.readBytes(filename, nameLen);
  filename[nameLen] = '\0';

  uint32_t fileSize = 0;
  input.readBytes((char*)&fileSize, sizeof(fileSize));

  // Create full path
  String fullPath = String(MODEL_DIR) + filename;

  // Open file for writing
  File file = SPIFFS.open(fullPath, FILE_WRITE);
  if (!file) {
    Serial.printf("❌ Failed to open %s for writing!\n", fullPath.c_str());
    return;
  }

  Serial.printf("📦 Receiving file: %s (%u bytes)\n", filename, fileSize);

  // Receive and write bytes
  uint32_t received = 0;
  unsigned long start = millis();

  while (received < fileSize) {
    if (input.available()) {
      uint8_t b = input.read();
      file.write(b);
      received++;
    }
  }

  file.close();
  Serial.printf("✅ File %s saved (%lu ms)\n", fullPath.c_str(), millis() - start);
}

// --- Utility to delete old models ---
void deleteModel(const char *filename) {
  String path = String(MODEL_DIR) + filename;
  if (SPIFFS.exists(path)) {
    SPIFFS.remove(path);
    Serial.printf("🗑 Deleted model: %s\n", filename);
  } else {
    Serial.printf("⚠️ Model not found: %s\n", filename);
  }
}

// Adjust to your model output length (e.g. 3 for dx, dy, clickProb)
#define MODEL_OUTPUTS 3

void readAndSendSensorData() {
  // Exit if no Bluetooth connection
  if (!isBluetoothConnected) return;

  // === 1. Read EMG analog data ===
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) {
    sensorValues[i] = analogRead(sensorPins[i]);
  }

  // === 2. Normalize and copy inputs into model tensor ===
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) {
    // Normalize ADC (0–4095) → float 0.0–1.0
    inputTensor->data.f[i] = (float)sensorValues[i] / 4095.0f;
  }

  // === 3. Run inference ===
  TfLiteStatus invokeStatus = interpreter->Invoke();
  if (invokeStatus != kTfLiteOk) {
    Serial.println("❌ Inference failed!");
    return;
  }

  // === 4. Collect model output ===
  float results[MODEL_OUTPUTS];
  for (int i = 0; i < MODEL_OUTPUTS; i++) {
    results[i] = outputTensor->data.f[i];
  }

  // === 5. Send results over Bluetooth ===
  // Example: "0.1200,-0.0340,0.8100"
  String packet;
  for (int i = 0; i < MODEL_OUTPUTS; i++) {
    packet += String(results[i], 4);
    if (i < MODEL_OUTPUTS - 1) packet += ",";
  }

  SerialBT.println(packet);

  // === 6. Optional: short delay to stabilize rate (100 Hz) ===
  delay(10);
}


def handleFileUpload():
  if usbConnected or BluetoothConnected:
    receiveModel()

def receiveModel():
  for file in package:
    if file is json:
      manifest_file = file
    if file is tensorflowlite:
      moedl_file = file
  input_count = manifest_file[input_count]
  output_count = manifest_file[output_count]
  