#signature class

all_devices = []

class Signature:
	def __init__(self, raw):
		self.raw = raw

		hbytes = [raw[i:i+2] for i in range(0, len(raw), 2)]
		self.sladdr = int(hbytes[0], 16)
		hbytes = hbytes[1:len(hbytes)]

		self.regs = [0 if i=='??' else int(i,16) for i in hbytes]
		self.stable = [i!='??' for i in hbytes]

		#all_devices.append(self)

	def dump(self):

		#print slave addr
		print("device 0x%02X:" % self.sladdr)

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