#

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

		DEVICE_LIBRARY.append(self)

	def printinfo(self):
		print('{} ({}) @ 0x%02x'.format(self.name, self.dtype, self.sladdr))

def build_dummy_library():
	I2cdev('TMP103', 'temp sensor', 0x48, [[0x10,0xF5], [0x12,0x03]])
	I2cdev('AYYLM40', 'little green man', 0x73, [[0x08,0x77]])
	I2cdev('LIS3MDL', 'accelerometer', 0x09, [[0x18, 0x3D]])

def prepare_library():
	#split library into bins for each slave addr
	global DEVICE_LIBRARY
	DEVICE_LIBRARY = [list(filter(lambda n:n.sladdr == i, DEVICE_LIBRARY)) for i in range(0,0x80)]
	#pdb.set_trace()
	print(DEVICE_LIBRARY)
