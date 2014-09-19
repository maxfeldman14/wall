int frame[20] = {0};
int frame_size = 8;
int frame_index = -3;

void setup() {
  Serial.begin(9600);
  for(int i = 0; i < 8; i++) {
    pinMode(led(i), OUTPUT);
  }
}

int led(int i) {
  return i + 22;
}

void loop() {
  while(Serial.available() > 0) {
    readByte();
  }
  drawFrame();
}

void readByte() {
  int byte = Serial.read();
  switch(frame_index) {
  case -3:
    if (byte == 13) {
      frame_index++;
    }
    return;
  case -2:
    if (byte == 37) {
      frame_index++;
    } else {
      frame_index = -3;
    }
    return;
  case -1:
    if (byte > 0 && byte <= 20)
    frame_size = byte;
    frame_index++;
    return;
  default:
    frame[frame_index] = byte;
    frame_index++;
    frame_index = frame_index == frame_size ? -3 : frame_index;
    break;
  }
}

void drawFrame() {
  int thresh = micros() % 256;
  for (int i = 0; i < frame_size; i++) {
    digitalWrite(led(i), frame[i] > thresh ? HIGH : LOW);
  }
}
