

import serial
import serial.tools.list_ports
import time
from enum import Enum

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
	print('opening port... ', end="")
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
	code = int(spec.strip(unwanted))
	if(code >= len(mes_list)):
		print('invalid message code (', spec, ')')
		exit()
	return mes_list[code]

#if it starts with "err", it's an error
#if it starts with "signature", etc etc
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
		else:
			exit(0)
	#elif(resp.find("signature")==0)
	else:
		print(resp)

#############################################################

ser = connect_to_duiner()
if(not start_scan(ser)):
	print('arduino didn\'t give the expect respond to \"go duiner go\". maybe it has the wrong firmware loaded?')
	exit()

while 1:
	resp = ser.readline().decode()
	handle_response(resp)

ser.close()
