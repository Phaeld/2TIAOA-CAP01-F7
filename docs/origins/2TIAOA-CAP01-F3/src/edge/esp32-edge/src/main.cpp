/*
Project: CardioIA - Part 1 (Edge Computing)
Platform: ESP32
Environment: Wokwi / Arduino IDE
AUTHOR: Raphael da Silva RM: 561452
GROUP: São Paulo e Interior

Objective:
- Read sensors from a simulated health smartwatch
- Store data locally on microSD card
- Use RAM buffer as fallback/demonstration
- Simulate Wi-Fi connectivity
- Synchronize data when the connection returns
*/

#include <Arduino.h>
#include <DHTesp.h>
#include <Wire.h>
#include <MPU6050.h>
#include <SPI.h>
#include <SD.h>

// =====================================================
// PINOUT AND CONFIGURATIONS
// =====================================================

// Sensors and actuators
static const uint8_t DHT_PIN = 15;
static const uint8_t HEART_RATE_PIN = 34;
static const uint8_t EMERGENCY_BUTTON_PIN = 4;
static const uint8_t ALERT_LED_PIN = 13;

// SPI - microSD
static const uint8_t SD_CS_PIN = 5;
static const uint8_t SD_SCK_PIN = 18;
static const uint8_t SD_MISO_PIN = 19;
static const uint8_t SD_MOSI_PIN = 23;

// I2C - MPU6050
static const uint8_t MPU_SDA_PIN = 21;
static const uint8_t MPU_SCL_PIN = 22;

// Timing
static const uint32_t SENSOR_READ_INTERVAL_MS = 2000;
static const uint32_t WIFI_CHECK_INTERVAL_MS = 8000;

// Alert Thresholds
static const float TEMPERATURE_ALERT_C = 38.0f;
static const uint8_t HEART_RATE_ALERT_BPM = 120;

// Buffer in RAM
static const uint16_t MAX_BUFFER_RECORDS = 100;

// File name on SD card
static const char *SD_FILE_PATH = "/data.csv";

// =====================================================
// OBJECTS OF THE SENSORS
// =====================================================

DHTesp dhtSensor;
MPU6050 mpuSensor;
SPIClass sdSpi(VSPI);

// =====================================================
// DATA STRUCTURES
// =====================================================

struct HealthRecord {
  uint32_t timestampMs;
  float temperatureC;
  float humidityPercent;
  uint8_t heartRateBpm;
  bool movementDetected;
  bool emergencyPressed;
};

// =====================================================
// GLOBAL VARIABLES
// =====================================================

// General condition
bool wifiConnected = false;
bool sdAvailable = false;

// Time control
uint32_t lastSensorReadMs = 0;
uint32_t lastWifiCheckMs = 0;

// Current reading
float currentTemperatureC = 0.0f;
float currentHumidityPercent = 0.0f;
uint8_t currentHeartRateBpm = 0;
bool currentMovementDetected = false;
bool currentEmergencyPressed = false;

// Circular buffer in RAM (fallback)
HealthRecord recordBuffer[MAX_BUFFER_RECORDS];
uint16_t bufferHead = 0;
uint16_t bufferTail = 0;
uint16_t bufferedCount = 0;

// =====================================================
// PROTOTYPES
// =====================================================

// Initialization
void initializePins();
void initializeSensors();
void initializeSD();
void initializeSystem();

// Sensor reading
void readDhtValues(float &temperatureC, float &humidityPercent);
uint8_t readHeartRate();
bool readMovement();
bool readEmergencyButton();

// Registration and processing
HealthRecord createHealthRecord();
void processCurrentReading();
void evaluateAlerts(const HealthRecord &record);

// Buffer in RAM
bool storeRecordInBuffer(const HealthRecord &record);
bool isBufferFull();
bool isBufferEmpty();
void removeOldestBufferRecord();
void clearBuffer();
void syncBufferRecords();

// microSD
bool saveRecordToSD(const HealthRecord &record);
void ensureSDFileHeader();
void syncSDRecords();
void clearSDFile();

// Connectivity and transmission
void simulateWifiStatus();
void sendRecordToCloud(const HealthRecord &record);

// Utilities
void printCurrentReading(const HealthRecord &record);
void printSystemStatus();
void printCsvRecord(const HealthRecord &record);
const char *boolToText(bool value);

// =====================================================
// SETUP
// =====================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  initializeSystem();

  Serial.println("======================================");
  Serial.println("CardioIA - Edge Computing started");
  Serial.println("======================================");
}

// =====================================================
// LOOP
// =====================================================

void loop() {
  const uint32_t currentMs = millis();

  // Periodic sensor reading
  if (currentMs - lastSensorReadMs >= SENSOR_READ_INTERVAL_MS) {
    lastSensorReadMs = currentMs;
    processCurrentReading();
  }

  // Periodic simulation of connectivity
  if (currentMs - lastWifiCheckMs >= WIFI_CHECK_INTERVAL_MS) {
    lastWifiCheckMs = currentMs;

    simulateWifiStatus();
    printSystemStatus();

    // If you're online, it will sync everything that was pending
    if (wifiConnected) {
      syncSDRecords();
      syncBufferRecords();
    }
  }
}

// =====================================================
// INITIALIZATION
// =====================================================

void initializePins() {
  pinMode(EMERGENCY_BUTTON_PIN, INPUT_PULLUP);
  pinMode(ALERT_LED_PIN, OUTPUT);
  digitalWrite(ALERT_LED_PIN, LOW);
}

void initializeSensors() {
  dhtSensor.setup(DHT_PIN, DHTesp::DHT22);

  Wire.begin(MPU_SDA_PIN, MPU_SCL_PIN);
  mpuSensor.initialize();

  if (mpuSensor.testConnection()) {
    Serial.println("[MPU6050] Sensor initialized successfully.");
  } else {
    Serial.println("[MPU6050] Sensor initialization failed.");
  }
}

void initializeSD() {
  sdSpi.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);

  if (!SD.begin(SD_CS_PIN, sdSpi)) {
    Serial.println("[SD] Initialization failed.");
    sdAvailable = false;
    return;
  }

  sdAvailable = true;
  Serial.println("[SD] Initialization success.");
  ensureSDFileHeader();
}

void initializeSystem() {
  initializePins();
  initializeSensors();
  initializeSD();
  clearBuffer();
}

// =====================================================
// SENSOR READINGS
// =====================================================

void readDhtValues(float &temperatureC, float &humidityPercent) {
  // Single DHT reading to avoid redundancy
  TempAndHumidity data = dhtSensor.getTempAndHumidity();

  temperatureC = data.temperature;
  humidityPercent = data.humidity;

  if (isnan(temperatureC) || isnan(humidityPercent)) {
    Serial.println("[DHT22] Failed reading sensor values.");
    temperatureC = -1.0f;
    humidityPercent = -1.0f;
  }
}

uint8_t readHeartRate() {
  // Heartbeat simulation via potentiometer
  const int16_t analogValue = analogRead(HEART_RATE_PIN);

  // Maps to a plausible BPM range.
  const long mappedValue = map(analogValue, 0, 4095, 60, 140);

  return (uint8_t)mappedValue;
}

bool readMovement() {
  // Simple reading of the MPU6050 to simulate movement
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpuSensor.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // Simple limit to indicate movement
  const int16_t movementThreshold = 2000;

  if (abs(ax) > movementThreshold || abs(ay) > movementThreshold || abs(az) > movementThreshold) {
    return true;
  }

  return false;
}

bool readEmergencyButton() {
  // As it is in INPUT_PULLUP:
  // pressed = LOW
  return digitalRead(EMERGENCY_BUTTON_PIN) == LOW;
}

// =====================================================
// CREATION AND PROCESSING OF RECORDS
// =====================================================

HealthRecord createHealthRecord() {
  HealthRecord record;

  record.timestampMs = millis();
  record.temperatureC = currentTemperatureC;
  record.humidityPercent = currentHumidityPercent;
  record.heartRateBpm = currentHeartRateBpm;
  record.movementDetected = currentMovementDetected;
  record.emergencyPressed = currentEmergencyPressed;

  return record;
}

void processCurrentReading() {
  // Collect the current values
  readDhtValues(currentTemperatureC, currentHumidityPercent);
  currentHeartRateBpm = readHeartRate();
  currentMovementDetected = readMovement();
  currentEmergencyPressed = readEmergencyButton();

  // Set up the registry
  HealthRecord record = createHealthRecord();

  // Shows current reading
  printCurrentReading(record);

  // Assess alerts locally
  evaluateAlerts(record);

  // Strategy:
  // Online -> sends immediately
  // Offline -> saves to SD card
  // If SD card fails -> saves to RAM buffer
  if (wifiConnected) {
    sendRecordToCloud(record);
  } else {
    bool storedOnSD = saveRecordToSD(record);

    if (!storedOnSD) {
      storeRecordInBuffer(record);
      Serial.println("[EDGE] Record stored in RAM fallback.");
    }
  }
}

void evaluateAlerts(const HealthRecord &record) {
  bool alertActive = false;

  if (record.temperatureC > TEMPERATURE_ALERT_C) {
    alertActive = true;
    Serial.println("[ALERT] Temperature above safe limit.");
  }

  if (record.heartRateBpm > HEART_RATE_ALERT_BPM) {
    alertActive = true;
    Serial.println("[ALERT] Heart rate above safe limit.");
  }

  if (record.emergencyPressed) {
    alertActive = true;
    Serial.println("[CRITICAL ALERT] Emergency button pressed.");
  }

  // Local LED indicates edge alert
  digitalWrite(ALERT_LED_PIN, alertActive ? HIGH : LOW);
}

// =====================================================
// BUFFER RAM (FALLBACK / DEMONSTRATION)
// =====================================================

bool storeRecordInBuffer(const HealthRecord &record) {
  if (isBufferFull()) {
  // FIFO Strategy:
  // Remove the oldest to make room
    removeOldestBufferRecord();
  }

  recordBuffer[bufferTail] = record;
  bufferTail = (bufferTail + 1) % MAX_BUFFER_RECORDS;
  bufferedCount++;

  return true;
}

bool isBufferFull() {
  return bufferedCount >= MAX_BUFFER_RECORDS;
}

bool isBufferEmpty() {
  return bufferedCount == 0;
}

void removeOldestBufferRecord() {
  if (!isBufferEmpty()) {
    bufferHead = (bufferHead + 1) % MAX_BUFFER_RECORDS;
    bufferedCount--;
  }
}

void clearBuffer() {
  bufferHead = 0;
  bufferTail = 0;
  bufferedCount = 0;
}

void syncBufferRecords() {
  if (isBufferEmpty()) {
    Serial.println("[SYNC RAM] No pending records.");
    return;
  }

  Serial.println("[SYNC RAM] Sending buffered records...");

  while (!isBufferEmpty()) {
    HealthRecord &record = recordBuffer[bufferHead];
    sendRecordToCloud(record);
    removeOldestBufferRecord();
  }

  Serial.println("[SYNC RAM] Synchronization finished.");
}

// =====================================================
// MICROSD (MAIN STORAGE)
// =====================================================

void ensureSDFileHeader() {
  if (!sdAvailable) {
    return;
  }

  if (!SD.exists(SD_FILE_PATH)) {
    File file = SD.open(SD_FILE_PATH, FILE_WRITE);

    if (!file) {
      Serial.println("[SD] Failed to create file header.");
      return;
    }

    file.println("timestamp_ms,temperature_c,humidity_percent,heart_rate_bpm,movement_detected,emergency_pressed");
    file.close();

    Serial.println("[SD] CSV header created.");
  }
}

bool saveRecordToSD(const HealthRecord &record) {
  if (!sdAvailable) {
    return false;
  }

  File file = SD.open(SD_FILE_PATH, FILE_APPEND);

  if (!file) {
    Serial.println("[SD] Failed to open file for append.");
    return false;
  }

  file.print(record.timestampMs);
  file.print(",");
  file.print(record.temperatureC, 2);
  file.print(",");
  file.print(record.humidityPercent, 2);
  file.print(",");
  file.print(record.heartRateBpm);
  file.print(",");
  file.print(record.movementDetected ? 1 : 0);
  file.print(",");
  file.println(record.emergencyPressed ? 1 : 0);

  file.close();

  Serial.println("[SD] Record saved locally.");
  return true;
}

void syncSDRecords() {
  if (!sdAvailable) {
    Serial.println("[SYNC SD] SD not available.");
    return;
  }

  if (!SD.exists(SD_FILE_PATH)) {
    Serial.println("[SYNC SD] No file found.");
    return;
  }

  File file = SD.open(SD_FILE_PATH, FILE_READ);

  if (!file) {
    Serial.println("[SYNC SD] Failed to open file for read.");
    return;
  }

  Serial.println("[SYNC SD] Sending records stored on SD...");

  bool isFirstLine = true;

  while (file.available()) {
    String line = file.readStringUntil('\n');
    line.trim();

    if (line.length() == 0) {
      continue;
    }

    // Ignore CSV header
    if (isFirstLine) {
      isFirstLine = false;
      if (line.startsWith("timestamp_ms")) {
        continue;
      }
    }

    // In this step, the transfer to the cloud is simulated by the Serial number
    Serial.print("[CLOUD FROM SD] ");
    Serial.println(line);
  }

  file.close();
  clearSDFile();

  Serial.println("[SYNC SD] Synchronization finished.");
}

void clearSDFile() {
  if (!sdAvailable) {
    return;
  }

  if (SD.exists(SD_FILE_PATH)) {
    SD.remove(SD_FILE_PATH);
    Serial.println("[SD] Local file cleared after sync.");
  }

  // Recreate header for future recordings
  ensureSDFileHeader();
}

// =====================================================
// CONNECTIVITY AND SENDING
// =====================================================

void simulateWifiStatus() {
// Simple simulation:
// Alternates between online and offline with each check cycle
  wifiConnected = !wifiConnected;

  if (wifiConnected) {
    Serial.println("[NETWORK] Wi-Fi connected.");
  } else {
    Serial.println("[NETWORK] Wi-Fi disconnected.");
  }
}

void sendRecordToCloud(const HealthRecord &record) {
  // In this stage of the activity, the sending is simulated by Serial.println
  Serial.println("----- CLOUD RECORD -----");
  Serial.print("timestamp_ms: ");
  Serial.println(record.timestampMs);

  Serial.print("temperature_c: ");
  Serial.println(record.temperatureC, 2);

  Serial.print("humidity_percent: ");
  Serial.println(record.humidityPercent, 2);

  Serial.print("heart_rate_bpm: ");
  Serial.println(record.heartRateBpm);

  Serial.print("movement_detected: ");
  Serial.println(boolToText(record.movementDetected));

  Serial.print("emergency_pressed: ");
  Serial.println(boolToText(record.emergencyPressed));
  Serial.println("------------------------");
}

// =====================================================
// UTILITIES
// =====================================================

void printCurrentReading(const HealthRecord &record) {
  Serial.println("===== CURRENT READING =====");
  Serial.print("Temperature (C): ");
  Serial.println(record.temperatureC, 2);

  Serial.print("Humidity (%): ");
  Serial.println(record.humidityPercent, 2);

  Serial.print("Heart Rate (BPM): ");
  Serial.println(record.heartRateBpm);

  Serial.print("Movement: ");
  Serial.println(boolToText(record.movementDetected));

  Serial.print("Emergency: ");
  Serial.println(boolToText(record.emergencyPressed));
  Serial.println("===========================");
}

void printSystemStatus() {
  Serial.println("===== SYSTEM STATUS =====");
  Serial.print("Wi-Fi: ");
  Serial.println(wifiConnected ? "CONNECTED" : "DISCONNECTED");

  Serial.print("SD available: ");
  Serial.println(sdAvailable ? "YES" : "NO");

  Serial.print("Buffered records in RAM: ");
  Serial.println(bufferedCount);

  Serial.println("=========================");
}

void printCsvRecord(const HealthRecord &record) {
  Serial.print(record.timestampMs);
  Serial.print(",");
  Serial.print(record.temperatureC, 2);
  Serial.print(",");
  Serial.print(record.humidityPercent, 2);
  Serial.print(",");
  Serial.print(record.heartRateBpm);
  Serial.print(",");
  Serial.print(record.movementDetected ? 1 : 0);
  Serial.print(",");
  Serial.println(record.emergencyPressed ? 1 : 0);
}

const char *boolToText(bool value) {
  return value ? "true" : "false";
}