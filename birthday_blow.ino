int sensor = 2; 
int led = 13; 

// Tuning variables
const int MIN_PULSES  = 1;     
const int WINDOW_MS   = 200;   
const int DEBOUNCE_MS = 400;  

int pulseCount = 0;
unsigned long windowStart = 0;
unsigned long lastTrigger = 0;

// Track the state of the "candle"
boolean is_on = true; 

void setup() {
  Serial.begin(9600);
  pinMode(sensor, INPUT_PULLUP); 
  pinMode(led, OUTPUT); 
  
  // Start with the LED ON (the candle is lit)
  digitalWrite(led, HIGH);
  Serial.println("READY"); 
}

void loop() {
  int data = digitalRead(sensor); 
  unsigned long now = millis();

  // 1. Detect Sound
  if (data == HIGH) {
    if (now - windowStart > WINDOW_MS) {
      pulseCount = 0;
      windowStart = now;
    }
    pulseCount++;
    delay(10); 
  }

  // 2. The Toggle Event
  if (pulseCount >= MIN_PULSES && (now - lastTrigger) > DEBOUNCE_MS) {
    
    // Toggle the variable
    is_on = !is_on; 
    
    // Apply the toggle to the physical LED
    digitalWrite(led, is_on ? HIGH : LOW);
    
    // Tell Python what happened
    Serial.println("BLOW"); 
    
    // Reset counters and set the debounce timer
    pulseCount = 0;
    lastTrigger = now;
    
    // A small delay here helps prevent the sound of the 
    // breath from triggering a "double toggle"
    delay(200); 
  }
}
