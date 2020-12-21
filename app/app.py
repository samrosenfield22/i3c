

import pdb

from arduino import *
from signature import * 
from i2cdev import *
#import i2cdev as i2c



def activate(dev):
	print('can\'t do that yet')

def manufacturer(dev):
	print(dev.manufacturer)

def datasheet(dev):
	print(dev.datasheet)

def helpmenu():
	for i,opt in enumerate(command_tbl):
		print(opt[0], end="")
		morespaces = 36 - len(str(opt[0]))
		print(' ' * morespaces, end="")
		print(opt[3])

#############################################################
#   main application
#############################################################

#
build_dummy_library()
prepare_library()
#pdb.set_trace()

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

#identify each device, print their info
#pdb.set_trace()
print('\nScan complete!')
print('Found {} devices:'.format(len(all_devices)))
for i,sig in enumerate(all_devices):
	if(sig.identify()):
		print('Device {}: '.format(i), end="")
		sig.printinfo()
	else:
		print('Device {}: unidentified, '.format(i), end="")
		sig.hexdump()

#
# each command has the following propertes: cmd strings, takes_arg, code, explanation

command_tbl = [
	[['a', 'activate'], True, 'activate(dev)', 'Configures the device, interacts with it'],
	#[['g', 'generate'], True, , 'Generates source code to use the device']
	[['m', 'mfg', 'manufacturer'], True, 'manufacturer(dev)', 'Prints the device manufacturer'],
	[['s', 'ds', 'datasheet'], True, 'datasheet(dev)', 'Prints the url to the device\'s datasheet'],
	[['d', 'hex', 'dump', 'hexdump'], True, 'sig.hexdump()', 'Prints the device\'s slave address and register contents'],
	#[['f', 'format'], True, , ]
	[['h', 'help'], False, 'helpmenu()', 'Prints this help menu'],
	[['e', 'exit'], False, 'break', 'Exits the interactive terminal']
]

print('\nlaunching interactive terminal...')
while 1:
	cmd = input('\n>>> ')

	sig = []
	dev = []
	arg = []
	if(' ' in cmd):

		cmd,arg = cmd.split(' ')
		if(arg != 'all'):
			devid = int(arg)
			if(devid >= len(all_devices)):
				print('Invalid device number, should be one of the following:')
				print(list(range(len(all_devices))))
				continue
			sig = all_devices[devid]
			dev = sig.device

	cmd_recognized = False
	for i,opt in enumerate(command_tbl):
		if(cmd in opt[0]):

			cmd_recognized = True

			#check arg
			if(opt[1]):
				if(not arg):
					print('Missing argument to command %s' % cmd)
					continue
				elif(not dev):
					print('Device %d wasn\'t found in the library' % devid)
					continue
			else:
				if(arg):
					print('Command %s doesn\'t take arguments' % cmd)
					continue
			
			#execute the command
			exec(opt[2])
			break

	if(not cmd_recognized):
		print('Unrecognized command: %s' % cmd)

print('all done!')
duiner.disconnect()


