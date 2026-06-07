#include <WiFi.h>
#include <WebServer.h>
#include <FastLED.h>

// WiFi
const char* ssid = "Adel";
const char* password = "12345678";

// LED strip
#define LED_PIN 5
#define NUM_LEDS 30

CRGB leds[NUM_LEDS];

WebServer server(80);

void handleValue() {

  Serial.println("Request Received");

  if (server.hasArg("d")) {

    int ledsOn = server.arg("d").toInt();

    Serial.print("Received Value = ");
    Serial.println(ledsOn);

    ledsOn = constrain(ledsOn, 0, 15);

    // Turn OFF all LEDs
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = CRGB::Black;
    }

    // Center position
    int center = NUM_LEDS / 2;

    // Light from center outward
    for (int i = 0; i < ledsOn; i++) {

      int left = center - i;
      int right = center + i;

      if (left >= 0)
        leds[left] = CRGB::Green;

      if (right < NUM_LEDS)
        leds[right] = CRGB::Green;
    }

    FastLED.show();

    Serial.print("LEDs ON = ");
    Serial.println(ledsOn);
  }

  server.send(200, "text/plain", "OK");
}

void setup() {

  Serial.begin(115200);

  Serial.println();
  Serial.println("ESP32 Starting...");

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);

  FastLED.clear();
  FastLED.show();

  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("================================");
  Serial.println("WiFi Connected!");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.println("================================");

  server.on("/value", handleValue);

  server.begin();

  Serial.println("HTTP Server Started");
}

void loop() {
  server.handleClient();
}