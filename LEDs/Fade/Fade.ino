int led1 = 12;
int led2 = 13;
int lvl = 0;

void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
  for(int i = 0; i < 10; i++) {
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
    delay(lvl);
    digitalWrite(led1, HIGH);
    digitalWrite(led2, HIGH);
    delay(20-lvl);
  }
  lvl++;
  lvl = lvl % 20;
}
