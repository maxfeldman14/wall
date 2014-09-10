/*
  Blink
  Turns on an LED on for one second, then off for one second, repeatedly.
 
  This example code is in the public domain.
 */
 
// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led1 = 13;
int led2 = 12;

// the setup routine runs once when you press reset:
void setup() {                
  // initialize the digital pin as an output.
  pinMode(led1, OUTPUT);   
  pinMode(led2, OUTPUT);  
}

// the loop routine runs over and over again forever:
void loop() {
  for(int i = 0; i < 50; i++) {
  digitalWrite(led1, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(led2, HIGH);
  delay(1);             // wait for a second
  digitalWrite(led1, LOW);    // turn the LED off by making the voltage LOW
  delay(9);               // wait for a 
  digitalWrite(led2, LOW);
  delay(10);
  }
  for(int i = 0; i < 50; i++) {
  digitalWrite(led1, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(led2, HIGH);
  delay(5);               // wait for a second
  digitalWrite(led1, LOW);    // turn the LED off by making the voltage LOW
  digitalWrite(led2, LOW);
  delay(15);               // wait for a 
  }
  for(int i = 0; i < 50; i++) {
  digitalWrite(led1, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(led2, HIGH);
  delay(1);               // wait for a second
  digitalWrite(led2, LOW);
  delay(9);
  digitalWrite(led1, LOW);    // turn the LED off by making the voltage LOW
  delay(10);               // wait for a 
  }
  digitalWrite(led1, HIGH);
  digitalWrite(led2, LOW);
  delay(1000);
  digitalWrite(led1, LOW);
  digitalWrite(led2, HIGH);
  delay(1000);
}
