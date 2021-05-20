import bencodepy
import sys
from struct import *

def decode_dictionary(d):
	tmp = {}
	for key,value in d.items():
		key = key.decode()
		t = type(value)
		if(key == 'pieces'):
			pieces = []
			for i in range(0,int(len(value)/20)):
				p = unpack("20s",value[:20])[0]
				pieces.append(p.hex())
				value = value[20:]
			value = pieces	
		elif(t is list):
			value = decode_list(value)
		elif(t is dict):
			value = decode_dictionary(value)
		elif(t is bytes):
			value = value.decode()
		tmp[key] = value
	d = tmp		
	return d				

def decode_list(l):
	tmp = []
	for x in l:
		t = type(x)
		if(t is list):
			tmp.append(decode_list(x))
		elif(t is dict):
			tmp.append(decode_dictionary(x))
		elif(t is bytes):
			tmp.append(x.decode())
	l = tmp							
	return l		

def decode_torrent(filename):
	f = open(sys.argv[1] , "rb")
	met = bencodepy.decode(f.read())
	f.close()
	return decode_dictionary(met)