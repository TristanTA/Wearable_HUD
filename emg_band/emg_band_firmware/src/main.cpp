// ==========================================================
// EMG_Band_V0 (BLE Edition for ESP32-S3)
// Boot -> BLE -> Load TFLM model from SPIFFS -> Stream inference
// Fallback: streams raw EMG CSV if no model is found.
// ==========================================================

#include <Arduino.h>
#include <NimBLEDevice.h>
#include "FS.h"
#include "SPIFFS.h"

// TensorFlow Lite Micro
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"



// ----------------- Hardware Config -----------------
#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

#define NUM_EMG_CHANNELS 3
int sensorPins[NUM_EMG_CHANNELS] = {A0, A1, A2};
#define BATTERY_SENSE_PIN A3

// ----------------- BLE Setup -----------------
#define SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

NimBLEServer* pServer;
NimBLECharacteristic* pCharacteristic;
bool deviceConnected = false;

class ServerCallbacks : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer*) override   { deviceConnected = true; }
  void onDisconnect(NimBLEServer*) override{ deviceConnected = false; }
};

// ----------------- TFLM Globals -----------------
namespace {
  constexpr size_t kTensorArenaSize = 60 * 1024;
  alignas(16) static uint8_t tensor_arena[kTensorArenaSize];

  const tflite::Model* g_model = nullptr;
  tflite::AllOpsResolver g_resolver;
  tflite::MicroInterpreter* g_interpreter = nullptr;
  TfLiteTensor* g_input = nullptr;
  TfLiteTensor* g_output = nullptr;

  uint8_t* g_model_buf = nullptr;
  size_t g_model_size = 0;
}

bool modelReady = false;
static const char* MODEL_DIR = "/models/";
static const char* BOOT_MODEL = "/models/boot.tflite";

// ----------------- Forward Decls -----------------
void loadModelFromSPIFFS(const char* path);
void receiveModelFile(Stream& input, const char* defaultName);
void readAndSend();
void reportBattery();
void printModelIO();
void safeBlinkError();

// ==========================================================
// SETUP
// ==========================================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n=== EMG_BAND_V0 (BLE) ===");

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) pinMode(sensorPins[i], INPUT);

  // Mount SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS mount failed");
    safeBlinkError();
  } else {
    Serial.println("SPIFFS mounted");
  }

  // BLE Init
  NimBLEDevice::init("EMG_Band_V0");
  pServer = NimBLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());
  NimBLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
      CHARACTERISTIC_UUID, NIMBLE_PROPERTY::NOTIFY);
  pService->start();
  pServer->getAdvertising()->start();
  Serial.println("BLE advertising as EMG_Band_V0");

  // Load default model if available
  if (SPIFFS.exists(BOOT_MODEL)) {
    loadModelFromSPIFFS(BOOT_MODEL);
  } else {
    Serial.println("No model found; streaming raw EMG data.");
  }
}

// ==========================================================
// LOOP
// ==========================================================
unsigned long lastBattery = 0;
const uint32_t periodMs = 5; // ~200 Hz

void loop() {
  if (Serial.available())    receiveModelFile(Serial, "usb_model.tflite");
  if (millis() - lastBattery > 5000) {
    reportBattery();
    lastBattery = millis();
  }

  static unsigned long lastTick = 0;
  if (millis() - lastTick >= periodMs) {
    lastTick += periodMs;
    readAndSend();
  }
}

// ==========================================================
// CORE FUNCTIONS
// ==========================================================

void readAndSend() {
  int adc[NUM_EMG_CHANNELS];
  for (int i = 0; i < NUM_EMG_CHANNELS; i++) adc[i] = analogRead(sensorPins[i]);

  char msg[64];
  if (!modelReady) {
    sprintf(msg, "%d,%d,%d\n", adc[0], adc[1], adc[2]);
  } else {
    const int inElems = g_input->bytes / sizeof(float);
    for (int i = 0; i < NUM_EMG_CHANNELS && i < inElems; i++)
      g_input->data.f[i] = float(adc[i]) / 4095.0f;

    if (g_interpreter->Invoke() == kTfLiteOk) {
      const int outElems = g_output->bytes / sizeof(float);
      msg[0] = '\0';
      for (int i = 0; i < outElems; i++) {
        char tmp[16];
        sprintf(tmp, "%.6f%s", g_output->data.f[i], (i < outElems - 1) ? "," : "\n");
        strcat(msg, tmp);
      }
    } else {
      strcpy(msg, "ERR:invoke\n");
    }
  }

  Serial.print(msg);
  if (deviceConnected) {
    pCharacteristic->setValue((uint8_t*)msg, strlen(msg));
    pCharacteristic->notify();
  }
}

void loadModelFromSPIFFS(const char* path) {
  File f = SPIFFS.open(path, FILE_READ);
  if (!f) {
    Serial.printf("Model open failed: %s\n", path);
    modelReady = false;
    return;
  }
  if (g_model_buf) { free(g_model_buf); }
  g_model_size = f.size();
  g_model_buf = (uint8_t*)malloc(g_model_size);
  if (!g_model_buf) {
    Serial.println("Model malloc failed");
    f.close();
    modelReady = false;
    return;
  }
  f.read(g_model_buf, g_model_size);
  f.close();

  g_model = tflite::GetModel(g_model_buf);
  if (g_model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Schema mismatch");
    modelReady = false;
    return;
  }

  static tflite::MicroInterpreter static_interpreter(g_model, g_resolver, tensor_arena, kTensorArenaSize);
  g_interpreter = &static_interpreter;
  if (g_interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("AllocateTensors failed");
    modelReady = false;
    return;
  }

  g_input = g_interpreter->input(0);
  g_output = g_interpreter->output(0);
  modelReady = true;
  Serial.printf("Model loaded: %s (%u bytes)\n", path, (unsigned)g_model_size);
  printModelIO();
}

void receiveModelFile(Stream& input, const char* defaultName) {
  if (input.available() < 1) return;
  input.setTimeout(2000);

  uint8_t nameLen = input.read();
  if (nameLen == 0 || nameLen > 60) return;

  char nameBuf[64] = {0};
  size_t got = input.readBytes(nameBuf, nameLen);
  if (got != nameLen) return;

  uint32_t fileSize = 0;
  if (input.readBytes((char*)&fileSize, sizeof(fileSize)) != sizeof(fileSize)) return;

  String fullPath = String(MODEL_DIR) + nameBuf;
  if (!fullPath.endsWith(".tflite")) fullPath += ".tflite";

  File out = SPIFFS.open(fullPath, FILE_WRITE);
  if (!out) return;

  uint32_t received = 0;
  while (received < fileSize) {
    if (input.available()) {
      uint8_t b = input.read();
      out.write(b);
      received++;
    }
  }
  out.close();
  Serial.printf("Saved %s\n", fullPath.c_str());
  loadModelFromSPIFFS(fullPath.c_str());
}

void printModelIO() {
  if (!g_input || !g_output) return;
  Serial.printf("Input: type %d bytes %d dims:", g_input->type, g_input->bytes);
  for (int i = 0; i < g_input->dims->size; i++) Serial.printf(" %d", g_input->dims->data[i]);
  Serial.println();
  Serial.printf("Output: type %d bytes %d dims:", g_output->type, g_output->bytes);
  for (int i = 0; i < g_output->dims->size; i++) Serial.printf(" %d", g_output->dims->data[i]);
  Serial.println();
}

void reportBattery() {
  int raw = analogRead(BATTERY_SENSE_PIN);
  float v = (raw / 4095.0f) * 3.3f * 2.0f;
  Serial.printf("Battery: %.2f V\n", v);
}

void safeBlinkError() {
  for (int i = 0; i < 6; i++) {
    digitalWrite(LED_BUILTIN, (i % 2) ? LOW : HIGH);
    delay(200);
  }
  digitalWrite(LED_BUILTIN, HIGH);
}
