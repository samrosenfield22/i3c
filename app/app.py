

import serial
import serial.tools.list_ports
import time
from enum import Enum

ErrorMessages = [
	"either a device is pulling SDA/SCL low, or the line(s) are disconnected!",
	"read abnormal bus voltages.\nis something pulling the bus low? are there pullup resistors?"
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
		print('couldn\'t open the port! is the arduino serial monitor open?')
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
	#if(not (response == 'ok\n'))
	#print('got response:', response)
	return (response == b'ok\r\n')
	#return False

def display_error(mes):
	errcode = int(mes.strip('err '))
	if(errcode >= len(ErrorMessages)):
		print('error w invalid err code')
	else:
		print(ErrorMessages[errcode])


#############################################################

ser = connect_to_duiner()
if(not start_scan(ser)):
	print('problem connecting to arduino')
	exit()

resp = ser.readline().decode()
if(resp.find("err")!=-1):
	display_error(resp)
	exit()

ser.close()
