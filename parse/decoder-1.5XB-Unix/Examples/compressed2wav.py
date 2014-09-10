#! /usr/bin/env python
"""Example:
Decoding a compressed audio file to PCM WAVE and saving the result."""

import decoder, wave, os

cfn = raw_input("Compressed audio file path: ")
cfn = os.path.normpath(cfn)
while not os.path.exists(cfn):
    print "File '"+cfn+"' does not exist!"
    cfn = raw_input("Compressed audio file path: ")
    cfn = os.path.normpath(cfn)

wfn = raw_input("Output wave file path: ")

fh = 0 # ForceHeader
if os.name=="posix" and cfn[-4:] in (".aac", ".m4a", ".m4b", ".mp4"): fh = 1

cf = decoder.open(cfn, fh)
wf = wave.open(wfn, "w")

print "Decoding; Please wait!"
decoder.copywaveobj(cf, wf)
print "Done!"
cf.close(); wf.close()
raw_input("Press enter to continue . . . ")