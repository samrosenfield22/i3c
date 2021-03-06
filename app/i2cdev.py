#

from arduino import *

import pdb

DEVICE_LIBRARY = []



class I2cdev:

	def __init__(self, name, dtype, sladdr, whoami, action="", manufacturer="", datasheet="", config=[]):

		self.name = name
		self.dtype = dtype
		self.manufacturer = manufacturer
		self.datasheet = datasheet

		#
		self.sladdr = sladdr
		self.whoami = whoami
		self.config = config
		self.action = action	#action shouldn't really have a default

		global DEVICE_LIBRARY
		DEVICE_LIBRARY.append(self)

	def activate(self, duiner):

		#write all config registers
		for i,cfg in enumerate(self.config):
			if(not duiner.write_reg(self.sladdr, cfg[0], cfg[1])):
				print('Failed readback after writing to register 0x%02X' % cfg[0])
				return False

		#read/write to action registers depending on the device dtype
		#i.e. if it's a sensor, we'll read them, if it's an output device like a switcher, write to them
		return True

	def printinfo(self):
		print('{} ({}) @ 0x%02x'.format(self.name, self.dtype) % self.sladdr)

def build_dummy_library():
	I2cdev('TMP103', 'temp sensor', 0x48, [[0x10,0xF5], [0x12,0x03]])
	I2cdev('AYYLM40', 'little green man', 0x73, [[0x08,0x77]])
	I2cdev('LIS3MDL', 'accelerometer', 0x09, [[0x18, 0x3D]])

def prepare_library():
	#split library into bins for each slave addr
	global DEVICE_LIBRARY
	DEVICE_LIBRARY = [list(filter(lambda n:n.sladdr == i, DEVICE_LIBRARY)) for i in range(0,0x80)]
	#pdb.set_trace()
	#print(id(DEVICE_LIBRARY))
	#print(DEVICE_LIBRARY)
	#print('\n\n')

def get_devices_matching_sladdr(sladdr):
	assert(len(DEVICE_LIBRARY) > sladdr)
	return DEVICE_LIBRARY[sladdr]
