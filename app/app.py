

import serial
import serial.tools.list_ports
import time
from enum import Enum
import pdb

from signature import * 

ErrorMessages = [
	"either a device is pulling SDA/SCL low, or the line(s) are disconnected!",
	"read abnormal bus voltages.\nis something pulling the bus low? are there pullup resistors?"
]

WarnMessages = [
	"Detected 3V3 I2C bus; this Arduino uses 5V logic. Is this what you want?"
]

#looks for a port whose manufacturer string contains 'Arduino'. returns that port, or an empty list if none is found
def get_duiner_port():
	ports = serial.tools.list_ports.comports()
	duiner = list(filter(lambda p:p.manufacturer.find('Arduino')!=-1, ports))
	if not duiner:
		return []
	else:
		return duiner[0]



def connect_to_duiner():
	#get the port
	duiner = get_duiner_port()
	if(not duiner):
		print("error: no duiner found")
		exit()
	print('arduino found at port:', duiner.name)

	#open it
	print('opening port... ', end="", flush=True)
	try:
		ser = serial.Serial(duiner.name, 9600, timeout=5)
	except:
		print('couldn\'t open the port! if the arduino serial monitor is open, close it and try again')
		exit()
	if(ser.is_open):
		ser.close()
	ser.open()
	time.sleep(3)
	print('done!')

	return ser

def start_scan(ser):
	ser.write(b'go duiner go\n')
	response = ser.readline()
	return (response == b'ok\r\n')

def getMessageFromSpec(spec, unwanted, mes_list):
	#code = int(spec.strip(unwanted))
	code = int(spec.removeprefix(unwanted))
	if(code >= len(mes_list)):
		print('invalid message code (', spec, ')')
		exit()
	return mes_list[code]

def handle_signature(sig):
	sig = sig.removeprefix("signature ")
	sig = sig.removesuffix("\r\n")

	s = Signature(sig)
	all_devices.append(s)
	#s.dump()

#if it starts with "err", it's an error
#if it starts with "signature", etc etc

#returns true if the response is "done" (tells main code to break out of the loop)
def handle_response(resp):
	if(resp.find("err")==0):
		errmes = getMessageFromSpec(resp, "err ", ErrorMessages)
		print('\nerror:', errmes)
		exit()
	elif(resp.find("warn")==0):
		warnmes = getMessageFromSpec(resp, "warn ", WarnMessages)
		print('\n---warning: ', warnmes, ' ---')
		confirm = input('press \'y\' to continue   ')
		if(confirm[0] == 'y'):
			print('confirmed!')
			ser.write(b'ok\n')
			return False
		else:
			exit(0)
	elif(resp.find("signature")==0):
		handle_signature(resp)
		return False
	elif(resp == "done\r\n"):
		return True
	else:
		print(resp)

#############################################################
#   main application
#############################################################

#connect to the arduino, command it to start scanning
ser = connect_to_duiner()
if(not start_scan(ser)):
	print('arduino didn\'t give the expect respond to \"go duiner go\". maybe it has the wrong firmware loaded?')
	exit()

#handle arduino's responses as it scans (signatures, warnings/errors, etc). loops until we receive the "done" response
while 1:
	resp = ser.readline().decode()
	if(handle_response(resp)):
		break

#this is where we'll identify each device. for now just dump them all
#pdb.set_trace()
#print(len(all_devices))
print('\nfound {} devices:'.format(len(all_devices)))
for i,dev in enumerate(all_devices):	#works with i,dev, but not with just dev ??
	dev.dump()

print('all done!')

ser.close()
