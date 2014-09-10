#! /usr/bin/env python
"""Example showing how to create music player using "decoder.py" and PyAudio library.
It shows how to open and play compressed audio file ( load(), reload(), play() ),
how to manipulate and monitor the playing ( play(), pause(), stop(), show() ) and how to navigate through the stream
( setpos(), forward(), backward(), jump() ).
Here are shown some other Python tricks as well.
Example is fully usable, but not yet totaly bugless.
There is a lot of threading errors under Linux because of its better and faster multiprocessing system.
On Windows, the thing works OK.
Example is here only to demonstrate the use of decoder.py.
"""

from thread import start_new_thread as thread
from time import sleep
import decoder, os, sys, pyaudio

# Get only one character from stdin without echoing it to stdout
try:
    # Windows version
    import msvcrt
    def prepareterm (): pass
    def restoreterm (): pass

    def getchar ():
        return msvcrt.getch()

except:
    # Unix version
    import termios
    import fcntl
    fd = sys.stdin.fileno()
    oldterm, oldflags = None, None

    def prepareterm ():
        """Turn off echoing"""
        global oldterm, oldflags
        if oldterm!=None and oldflags!=None: return
        oldterm = termios.tcgetattr(fd)
        newattr = oldterm[:] #termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    def restoreterm ():
        """Restore terminal to its previous state"""
        global oldterm, oldflags
        if oldterm==None and oldflags==None: return
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        oldterm, oldflags = None, None

    def getchar():
        """Get character from stdin"""
        prepareterm()
        while 1:
            try:
                c = sys.stdin.read(1)
                break
            except IOError: pass
        restoreterm()
        return c

def clear ():
    """Clear the screen"""
    os.system(("clear", "cls")[os.name=="nt"])

if os.name=="posix":
    # A try to avoid threading errors on Linux
    def raw_input (prompt):
        print prompt,
        txt = ""
        nrchars = -1
        while 1:
            c = getchar()
            if c=="\x1b": continue
            if c in ("\b", "\x7f"):
                txt = txt[:-1]
                if nrchars>=0: sys.stdout.write("\b \b"); nrchars -= 1
            else:
                txt += c; nrchars += 1
                sys.stdout.write(c)
            if c in ("\n", "\r"): txt = txt[:-1]; break
        return txt

running = 1
bufsize = 1024
if os.name!="nt": bufsize *= 25

p = pyaudio.PyAudio()

intro = """
L = Load
Z = Backward
X = Play
C = Pause
V = Stop
B = Forward
J = Jump
Q = Quit
"""

fileinfo = ""
clear()
print intro

cf = None     # Audio file (decoder.py)
stream = None # PyAudio stream
cpdata = None # Audio-data copying object (decoder.py)
timer = 0
blockshow = 0 # Stop showing playing status to stdout

def load (msg=None):
    """Load audio file"""
    global cf, stream, cpdata, blockshow, fileinfo
    blockshow = 1
    clear()
    print intro
    if msg: print >> sys.stderr, msg
    cfn = ""
    while 1:
        cfn = raw_input("Audio file path: ")
        if not cfn: break
        cfn = os.path.normpath(cfn)
        if os.path.exists(cfn): break
        print >> sys.stderr, "File '"+cfn+"' does not exist!"
    if not cfn:
        clear()
        print intro, fileinfo
        if cpdata:
            x = cpdata.status()
            if x==1: print "Playing"
            if x==-1: print "Paused"
            if x==0: print "Stopped"
        blockshow = 0
        return
    if os.path.splitext(cfn)[1] not in decoder.wildcard:
        return load("File format not supported!")
    wasplaying = 0
    if cpdata:
        if cpdata.status()==1: wasplaying = 1
        cpdata.stop(); cpdata.wait()
    if stream: stream.close()
    if cf: cf.close()
    fh = 0 # ForceHeader
    if os.name=="posix" and cfn[-4:] in (".aac", ".m4a", ".m4b", ".mp4"): fh = 1
    # 'faad' decoder on Linux needs forced headers to work correctly
    cf = decoder.open(cfn, fh)
    stream = p.open(format = p.get_format_from_width(cf.getsampwidth()),
        channels = cf.getnchannels(), 
        rate = cf.getframerate(),
        output = True)
    clear(); print intro
    print cfn, "loaded!"
    fileinfo = decoder.info(cfn).info.pprint()
    # Using function from module fileinfo.py through decoder.py
    print fileinfo
    if wasplaying: print "Playing"
    else: print "Stopped"
    blockshow = 0
    if wasplaying: play()

def reload ():
    """Reloads the file"""
    global cf
    try:
        if not cf: return
    except: return
    # Get the filename
    try:
        # Filename in fakewave object
        cfn = cf.obj.filename
        # cf.obj is a object returned by subprocess.Popen()
        # with added attribute (by 'decoder.py') "filename"
    except:
        # Filename in Wave_read or Aifc_read object
        cfn = cf._file.file.name
        # cf._file is a Chunk object within Wave/Aifc_read object,
        # cf._file.file is a normal file object where 'name' represents a filename
    try: cf.close()
    except: reload()
    fh = 0 # ForceHeader
    if os.name=="posix" and cfn[-4:] in (".aac", ".m4a", ".m4b", ".mp4"): fh = 1
    cf = decoder.open(cfn, fh)

def play ():
    """Play the loaded file"""
    global cpdata, timer
    if not stream:
        print >> sys.stderr, "No file loaded!"
        return
    if cpdata:
        if cpdata.status()==-1: cpdata.resume(); return
        else:
            stop()
            reload()
            # This may not work very well
            # Perhaps it would be better if it reloads without regarding the state of cpdata
    timer = 0
    cpdata = decoder.copywaveobj(cf, stream, bufsize=bufsize, blocking=0) # Start copying from file to stream

def pause ():
    """Pause/unpause the stream"""
    global cpdata
    if not cpdata: return
    if cpdata.status()==1: cpdata.pause()
    elif cpdata.status()==-1: cpdata.resume()
    else: pass

def stop ():
    """Stops the stream"""
    if cpdata:
        cpdata.stop(); cpdata.wait()
        stream.write(cf._framesize*cpdata.bufsize*"\x00") # Try to empty audio-card buffer

def setpos (val):
    """Sets the position in the stream (seconds)"""
    if not cpdata or not cf: return
    val = int(val)
    fr = cf.getframerate()
    if not hasattr(cf, "obj"):
        # It is a Wave/Aif_read object i.e. wave/aiff file
        return cf.setpos(val*fr)
    if val > timer:
        val -= timer
    else: reload() # Reload the file to set the stream to zero
    cf.readframes(val*fr) # Skip the val*fr frames

def forward ():
    """Forwards the stream for 10 seconds"""
    global timer
    if not cf or not cpdata: return
    if cpdata.status()==0: return
    t = timer+10
    if t > int(cf.getnframes()/cf.getframerate()): return
    setpos(t)
    timer = t

def backward ():
    """Backwards the stream for 10 seconds"""
    global timer, cpdata, blockshow
    if not cf or not cpdata: return
    t = timer-10
    if t < 0: return
    s = cpdata.status()
    if s==0: return
    if not hasattr(cf, "obj"):
        # It is a Wave/Aifc_read object
        setpos(t); timer = t; return
    blockshow = 1
    cpdata.stop(); cpdata.wait()
    setpos(t)
    if s!=0: cpdata = decoder.copywaveobj(cf, stream, bufsize=bufsize, blocking=0) # Start recopying
    if s==-1: cpdata.pause()
    timer = t
    clear()
    print intro, fileinfo
    if s==-1: print "Paused"
    if s==1: print "Playing"
    blockshow = 0

def jump ():
    """Jump to time"""
    global timer, cpdata, blockshow
    if not cf or not cpdata: return
    blockshow = 1
    l = cf.getnframes()/cf.getframerate()
    s = [str(int(l/60)), str(int(l%60))]
    if len(s[0])==1: s[0] = "0%s" % s[0]
    if len(s[1])==1: s[1] = "0%s" % s[1]
    print "\nDuration:", ":".join(s), "(%i sec)" % l
    s = cpdata.status()
    def end ():
        global blockshow
        clear()
        print intro, fileinfo
        if s==-1: print "Paused"
        if s==1: print "Playing"
        if s==0: print "Stopped"
        blockshow = 0
    try: t = map(int, raw_input("Jump to: ").strip().split(":"))
    except: return end()
    if len(t)>1: t = (t[0]*60)+t[1] # The value is in m:s or m:ss or mm:s or mm:ss format
    else: t = t[0] # The value is in seconds only
    if t < 0 or t > l: return end()
    if not hasattr(cf, "obj"):
        # It is a Wave/Aifc_read object
        setpos(t); timer = t; return end()
    cpdata.stop(); cpdata.wait()
    setpos(t)
    if s!=0: cpdata = decoder.copywaveobj(cf, stream, bufsize=bufsize, blocking=0) # Start recopying
    if s==-1: cpdata.pause()
    timer = t
    end()

def close ():
    """Terminate the program"""
    global blockshow
    blockshow = 1
    restoreterm()
    try: cpdata.stop(); cpdata.wait()
    except: pass
    try: cf.close()
    except: pass
    try: stream.close()
    except: pass
    p.terminate()
    clear()
    raw_input("\nPlayer terminated\n\nPress enter to continue . . . ")
    sys.exit()

def control ():
    """Waits for keypress"""
    global running
    while running:
        c = getchar().lower()
        if c=="l": load()
        if c=="z": backward()
        if c=="x": play()
        if c=="c": pause()
        if c=="v": stop()
        if c=="b": forward()
        if c=="j": jump()
        if c=="q": running = 0; break

def show ():
    """Shows changes and status of stream"""
    global timer
    stat = {0: "Stopped", 1: "Playing", -1: "Paused"}
    last = 0
    while running:
        if not cpdata: continue
        x = cpdata.status()
        if x!=last and not blockshow:
            clear()
            print intro, fileinfo
            print stat[x]; last = x
        s = "" # Avoid NameError (undefined 's') later; just a precaution
        if not blockshow:
            s = [str(int(timer/60)), str(int(timer%60))]
            if len(s[0])==1: s[0] = "0%s:" % s[0]
            if len(s[1])==1: s[1] = "0%s" % s[1]
            s = s[0]+s[1]
            if not blockshow: print s,
        if x==1: timer += 1
        if x==0: timer = 0
        cpdata.sleep(1)
        if not blockshow: sys.stdout.write(len(s)*"\b")

# Start the program
thread(show, ())
thread(control, ())
while running: sleep(1)
close()
