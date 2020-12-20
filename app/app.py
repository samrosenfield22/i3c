

import pdb

from arduino import *
from signature import * 
from i2cdev import *


#############################################################
#   main application
#############################################################

#
build_dummy_library()
prepare_library()
print(DEVICE_LIBRARY)
pdb.set_trace()

#connect to the arduino, command it to start scanning
duiner = Arduino()
if(not duiner.connect()):
	exit()
print('done!')
if(not duiner.scan()):
	exit()

#handle arduino's responses as it scans (signatures, warnings/errors, etc). loops until we receive the "done" response
while 1:
	resptype = duiner.interpret()
	if(resptype == ARD_FAIL):
		exit(0)
	elif(resptype == ARD_DONE):
		break

#this is where we'll identify each device. for now just dump them all
#pdb.set_trace()
print('\nfound {} devices:'.format(len(all_devices)))
for i,sig in enumerate(all_devices):	#works with i,dev, but not with just dev ??
	#sig.dump()
	if(sig.identify()):
		print('Device {}: ', i)
		sig.printinfo()
	else:
		print('Device {}: unidentified', i)
		sig.hexdump()

print('all done!')
duiner.disconnect()
