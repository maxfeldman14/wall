int led1 = 12;
int led2 = 13;
int lvl = 0;
int dir = 1;

void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
    if (lvl <= 10) {
      delayMicroseconds(lvl);
      digitalWrite(led1, HIGH);
      delayMicroseconds(20-lvl-lvl);
      digitalWrite(led2, HIGH);
      delayMicroseconds(lvl);
    } else {
      delayMicroseconds(20-lvl);
      digitalWrite(led2, HIGH);
      delayMicroseconds(lvl+lvl-20);
      digitalWrite(led1, HIGH);
      delayMicroseconds(20-lvl);
    }
  lvl+=dir;
  dir = lvl >= 20 && dir > 0? -1 : lvl <= 0 && dir < 0? 1 : dir;
}
