import decoder
import time
import sys
import struct
import pyaudio
import numpy
import math

filename = "song.mp3"
if len(sys.argv) > 1:
    filename = sys.argv[1]
mp3 = decoder.open(filename)
framerate = mp3.getframerate()
samplewidth = mp3.getsampwidth()
channels = mp3.getnchannels()
chunksize = 2048

# Loudness contour data, might want to adjust output accordingly
#f = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
#     1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500];
#
#Tf = [ 78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9, 14.4,
#       11.4, 8.6, 6.2, 4.4, 3.0, 2.2, 2.4, 3.5, 1.7, -1.3, -4.2,
#       -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3];
#
#contourfactors = [pow(10, (x/10)) for x in Tf]

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(samplewidth),
    channels=channels,
    rate=framerate,
    output=True)
fft = None

for i in xrange(mp3.getnframes()/chunksize):
    frames = mp3.readframes(chunksize)
    if len(frames) != chunksize * samplewidth * channels:
        break
    realsamples = []
    for j in xrange(chunksize):
        spot = j * samplewidth * channels
        sample = abs(struct.unpack("<h", frames[spot:spot+2])[0])
        realsamples.append(sample)
    fft = numpy.real(numpy.fft.rfft(realsamples))
    fullbars = []
    bars = []
    currsample = 1
    for j in xrange(10):
        total = 0
        for k in xrange(pow(2, j)):
            total += abs(fft[currsample])
            currsample += 1
        fullbars.append(int(math.sqrt(total))/50)
    for j in xrange(5):
      bars.append((fullbars[j*2] + fullbars[(j*2)+1])/2)

    print chr(27) + "[2J",
    print "\033[0;0H",
    for bar in bars:
        val = min(bar, 65)
        partial = val % 16
        val = (int((val+8)/16)) * 16
        dots = "." * val
        last = ''
        if partial != 0:
            dots += ''.join(['.' if x % partial == 0 else ' ' for x in xrange(16)])
        print dots
    sys.stdout.flush()
    stream.write(frames)
