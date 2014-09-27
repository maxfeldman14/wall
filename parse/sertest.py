from serial import Serial
import time

ser = Serial('/dev/ttyACM2', 9600, timeout=1)

while True:
  for i in xrange(16):
    data = [13, 37, 5] + [(x * 16) % 256 for x in xrange(i, i+5)]
    print data
    ser.write(bytearray(data))
    print ser.read(200);
    time.sleep(1)
