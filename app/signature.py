#signature class

from i2cdev import *
#import i2cdev as i2c

all_devices = []

class Signature:
	def __init__(self, raw):
		self.raw = raw
		self.device = []

		hbytes = [raw[i:i+2] for i in range(0, len(raw), 2)]
		self.sladdr = int(hbytes[0], 16)
		hbytes = hbytes[1:len(hbytes)]

		self.regs = [0 if i=='??' else int(i,16) for i in hbytes]
		self.stable = [i!='??' for i in hbytes]

		all_devices.append(self)

	def identify(self):
		#self.hexdump()	#for now
		#return

		#global DEVICE_LIBRARY
		#print(len(DEVICE_LIBRARY))
		#print('searching for device w addr {} ({} total devices)'.format(self.sladdr, len(DEVICE_LIBRARY[self.sladdr])))
		#for dev in enumerate(DEVICE_LIBRARY[self.sladdr]):
		candidates = get_devices_matching_sladdr(self.sladdr)
		for i,dev in enumerate(candidates):
			if(self.__match(dev)):
				self.device = dev
				return True
			else:
				return False

	#checks if the signature matches a given i2cdev device
	def __match(self, dev):
		assert self.sladdr == dev.sladdr

		#match whoami regs
		for i,whoami in enumerate(dev.whoami):
			addr = whoami[0]
			if (self.regs[addr] != whoami[1]):
				return False
			if(not self.stable[addr]):
				return False
		return True
			
	def printinfo(self):
		assert(self.device)
		self.device.printinfo()

	def hexdump(self):

		#print slave addr
		print("slave addr = 0x%02X:" % self.sladdr)

		#print header
		print("\t", end="")
		for i in range(0, 0x10):
			if(i==8):
				print("  ", end="")
			print('%1X  ' % i, end="")

		#print hex
		for i,reg in enumerate(self.regs):
			if(i % 0x10 == 0):
				print("\n 0x%02X\t" % i, end="")
			elif(i % 0x8 == 0):
				print("  ", end="")

			if(self.stable[i] == False):
				print('??', end=" ")
			else:
				print('%02X ' % reg, end="")
		print("")