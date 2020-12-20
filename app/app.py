

import pdb

from arduino import *
from signature import * 


#############################################################
#   main application
#############################################################

#connect to the arduino, command it to start scanning
duiner = Arduino()
if(not duiner.connect()):
	exit()
print('done!')
if(not duiner.scan()):
	print('arduino didn\'t give the expect respond to \"go duiner go\". maybe it has the wrong firmware loaded?')
	exit()

#handle arduino's responses as it scans (signatures, warnings/errors, etc). loops until we receive the "done" response
while 1:
	resptype = duiner.interpret()
	if(resptype == RESP_FAIL):
		exit(0)
	elif(resptype == RESP_DONE):
		break

#this is where we'll identify each device. for now just dump them all
#pdb.set_trace()
print('\nfound {} devices:'.format(len(all_devices)))
for i,sig in enumerate(all_devices):	#works with i,dev, but not with just dev ??
	sig.dump()

print('all done!')
duiner.disconnect()
