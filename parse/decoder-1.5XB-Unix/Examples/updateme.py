#! /usr/bin/env python
"""Example showing how to relatively safely update decoder.py
This program have to be run in the directory of decoder.py which have to be writtable!
When updating, you need to have in mind five things.
First,  there may be no updates available.
Second, the problems with internet connection, DNS, servers or update script may appear.
Third,  the update() function may affect your files, if they have the same name as the new files comming with update.
Fourth, something may happen and the new version may not work as the old one despite the backward compatibility.
Fifth,  the update() does not remove the backup file. This must be done manualy, if everything is OK, after the update.
"""

import decoder, sys, os

print "Wellcome to the 'decoder.py' updater!"
print 40*"-"
print
# Check for existing backups
bls = []
for x in os.listdir(os.curdir):
    if x.startswith("decoder-") and x.endswith("-backup.zip"): bls.append(x)
bls.sort()
if bls:
    print len(bls), "file(s) found, which might be a decoder.py backup file(s)."
    print "If you choose to restore adecoder.py to the previous version,"
    print "the last file will be used ('"+bls[-1]+"') and deleted afterwards."
    while 1:
        yn = raw_input("Do you want to restore your files and roll back to the previous version? (y/n) ").strip().lower()
        if yn.startswith("n"): break
        if yn.startswith("y"):
            print "* Restoring . . ."
            decoder.restore(bls[-1][8:-11])
            try: os.remove(bls[-1])
            except: pass
            print "* Finished!"
            break
    print
print "* Checking for updates . . ."
udict = decoder.CheckForUpdates()
if not udict:
    print "A problem occured!"
    print "Make sure that you are connected to the internet and then try again."
    sys.exit()

if udict["__version__"] <= decoder.__version__:
    print "You have the newest version available!"
    sys.exit()

if os.name=="nt" and udict["new_win32"]=="no":
    print "You have the newest version available!"
    sys.exit()

if os.name!="nt" and udict["new_unix"]=="no":
    print "You have the newest version available!"
    sys.exit()

print "A new version is available!"
print "Current version:", decoder.__version__
print "    New version:", udict["__version__"]
while 1:
    yn = raw_input("Do you want to update decoder.py? (y/n) ").strip().lower()
    if yn.startswith("n"): sys.exit()
    if yn.startswith("y"): break
print
print "* Updating . . ."

def filedict ():
    """This helps checking whether any of your files had been overwritten
    in a process of updating."""
    # Make a list of files contained in a previous version
    ld = [x.strip() for x in udict[decoder.__version__.lower()+"-"+("unix", "win32")[os.name=="nt"]+"_filelist"].split(";")]
    ld = [x.replace("/", os.sep) for x in ld]
    # Create a list of your files
    ls = []
    for root, dirs, files in os.walk(os.curdir):
        ls += [os.path.join(root, x) for x in files]
    ls = [x[2:] for x in ls]
    # Remove the decoder.py files from the list of your files
    ld.append("decoder-"+decoder.__version__+"-backup.zip") # Backup is not 'your' file
    for x in ld:
        try: ls.remove(x)
        except: pass
    fdict = {}
    for x in ls:
        fdict[x] = os.path.getmtime(x)
    return ld, fdict

# ld --> list of important files for current version
# df --> dictionary of all files of current directory and its subdirectories
#        key = filename, value = modification time
ld, df = filedict()
ldd = {} # Modification time dictionary for decoder.py's files
for x in ld:
    try: ldd[x] = os.path.getmtime(x)
    except: pass
result = decoder.update(udict)
if result==0:
    print "Updating failed!"
    print "Restore will be tried, just in case!"
    print "* Restoring . . ."
    decoder.restore()
    print "* Finished!"
    sys.exit()
print "* Finished!"
ndf = filedict()[1]
nldd = {}
for x in ld:
    try: nldd[x] = os.path.getmtime(x)
    except: pass
nfiles = [] # new files
mfiles = [] # modified files
ufiles = [] # Updated files
dfk = df.keys()
dfk.sort()
ndfk = ndf.keys()
ndfk.sort()
for x in ndfk:
    if x not in dfk:
        nfiles.append(x)
        continue
    if df[x]!=ndf[x]: mfiles.append(x)

for x in ld:
    if x=="decoder-"+decoder.__version__+"-backup.zip": continue
    if ldd[x]!=nldd[x]: ufiles.append(x)
print
print len(ufiles), "file(s) updated!"
print "Updated files:"
for x in ufiles: print x
print
print "There are", len(nfiles), "new files added!"
if nfiles:
    print "Added files:"
    for x in nfiles: print x
print
if not mfiles:
    print "There are no overwritten files, except for files of decoder.py"
else:
    print "The updater overwrote", len(mfiles), "file(s) not belonging to 'decoder.py "+decoder.__version__+"'"
    print "Overwritten files:"
    for x in mfiles: print x
    print
    while 1:
        yn = raw_input("Do you want to restore your files and roll back to the previous version? (y/n) ").strip().lower()
        if yn.startswith("n"): break
        if yn.startswith("y"):
            print "* Restoring . . ."
            decoder.restore()
            print "* Finished!"
            sys.exit()
print "* Testing . . ."
try:
    execfile("decoder.py")
    # Now, check that everything is on its place
    # Very stupid and very simple as well:
    faad, flac, ffmpeg, lame, oggdec, wmadec, info
    open, acopen, fakewave, copywaveobj, CreateWaveHeader, CreateWaveHeaderFromFile
except Exception, e:
    print "The following error detected:", e
    print "* Restoring . . ."
    decoder.restore()
    print "* Finished!"
    sys.exit()
print "* Finished!"
print "It seems that everything went fine!"
while 1:
    yn = raw_input("Do you want to remove the backup file? (y/n) ").strip().lower()
    if yn.startswith("n"): sys.exit()
    if yn.startswith("y"): break
try: os.remove("decoder-"+decoder.__version__+"-backup.zip")
except: pass