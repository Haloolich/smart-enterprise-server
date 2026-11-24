#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

const char* MQTT_SERVER = "test.mosquitto.org";
const int MQTT_PORT = 1883;

const char* DEVICE_CODE = "ESP32_01";
const char* MQTT_TOPIC = "enterprise/sensors/reading";
const int GAS_PIN = 34;
const int LIGHT_PIN = 35;
const int PIR_PIN = 27;

WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHTesp dhtSensor;

void setup() {
    Serial.begin(115200);

    dhtSensor.setup(15, DHTesp::DHT22);

    pinMode(PIR_PIN, INPUT);

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi connected");

    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }

    mqttClient.loop();

    static unsigned long lastSend = 0;

    if (millis() - lastSend >= 5000) {
        lastSend = millis();

        TempAndHumidity data = dhtSensor.getTempAndHumidity();

        sendSensorData("temperature", data.temperature, "C");
        sendSensorData("humidity", data.humidity, "%");
        int gasValue = analogRead(GAS_PIN);

        sendSensorData("gas", gasValue, "raw");

        int lightValue = analogRead(LIGHT_PIN);

        sendSensorData("light", lightValue, "raw");

        int motionValue = digitalRead(PIR_PIN);
        sendSensorData("motion", motionValue, "bool");
    }
}

void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT...");

        if (mqttClient.connect("Wokwi_ESP32_01")) {
            Serial.println("connected");
        } else {
            Serial.print("failed, state=");
            Serial.println(mqttClient.state());
            delay(2000);
        }
    }
}

void sendSensorData(const char* sensorType, float value, const char* unit) {
    char payload[200];

    snprintf(
        payload,
        sizeof(payload),
        "{\"device_code\":\"%s\",\"sensor_type\":\"%s\",\"value\":%.2f,\"unit\":\"%s\"}",
        DEVICE_CODE,
        sensorType,
        value,
        unit
    );

    mqttClient.publish(MQTT_TOPIC, payload);

    Serial.println(payload);
}