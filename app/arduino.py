# arduino class

import serial
import serial.tools.list_ports
import time
#from enum import Enum

from signature import * 

class Arduino:

	#attempts to find the serial port with a device w manufacturer string containing "Arduino", and open that port.
	#returns True/False if the port was successfully opened
	def connect(self):
		self.portname = self.__get_portname()
		if(not self.portname):
			print("error: no duiner found")
			return False
		print('arduino found at port:', self.portname)

		#open it
		print('opening port... ', end="", flush=True)
		try:
			ser = serial.Serial(self.portname, 9600, timeout=5)
		except:
			print('couldn\'t open the port! if the arduino serial monitor is open, close it and try again')
			return False
		if(ser.is_open):
			ser.close()
		ser.open()
		time.sleep(3)

		self.port = ser
		return True

	def disconnect(self):
		self.port.close()

	#reads the response, takes the appropriate action
	#returns a ResponseType
	def interpret(self):
		resp = self.__read()

		if(resp.find("err")==0):
			errmes = getMessageFromSpec(resp, "err ", ErrorMessages)
			print('\nerror:', errmes)
			return RESP_FAIL
		elif(resp.find("warn")==0):
			warnmes = getMessageFromSpec(resp, "warn ", WarnMessages)
			print('\n---warning: ', warnmes, ' ---')
			confirm = input('press \'y\' to continue   ')
			if(confirm and confirm[0] == 'y'):
				print('confirmed!')
				self.__write('ok')
				return RESP_OTHER
			else:
				return RESP_FAIL
		elif(resp.find("signature")==0):
			resp = resp.removeprefix("signature ")
			Signature(resp)	#adds the signature to a list
			return RESP_OTHER
		elif(resp == "done"):
			return RESP_DONE
		else:
			print('unknown response:')
			print(resp)
			exit()

	def scan(self):
		self.__write('go duiner go')
		response = self.__read()
		return (response == 'ok')


	################ private methods ################

	def __write(self, str):
		cmd = (str + '\n').encode()
		self.port.write(cmd)

	def __read(self):
		resp = self.port.readline().decode()
		return resp.removesuffix('\r\n')

	#looks for a port whose manufacturer string contains 'Arduino'. returns that port, or an empty list if none is found
	def __get_portname(self):
		ports = serial.tools.list_ports.comports()
		theport = list(filter(lambda p:p.manufacturer.find('Arduino')!=-1, ports))
		if not theport:
			return []
		else:
			return theport[0].name


#types of arduino responses 
#class ResponseType(Enum):
RESP_DONE = 1
RESP_FAIL = 2
RESP_OTHER = 3

ErrorMessages = [
	"either a device is pulling SDA/SCL low, or the line(s) are disconnected!",
	"read abnormal bus voltages.\nis something pulling the bus low? are there pullup resistors?"
]

WarnMessages = [
	"Detected 3V3 I2C bus; this Arduino uses 5V logic. Is this what you want?"
]

def getMessageFromSpec(spec, unwanted, mes_list):
	#code = int(spec.strip(unwanted))
	code = int(spec.removeprefix(unwanted))
	if(code >= len(mes_list)):
		print('invalid message code (', spec, ')')
		exit()
	return mes_list[code]
