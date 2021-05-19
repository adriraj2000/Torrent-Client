import bencodepy
import sys

# As data is in buffer form this library will be used to pack and unpack data
from struct import *


def decode_dictionary(d):
    temp = {}
    for key, val in d.items():
        key = key.decode()
        if(key == 'pieces'):
            pieces = []
            # The ‘pieces’ element in the .torrent metafile 
            # includes a string of 20-byte hashes, one for each piece in the torrent
            for i in range(0, int(len(val)/20)):
                p = unpack("20s", val[:20])[0]
                pieces.append(p.hex())
                val = val[20:0]
        elif type(val) is list:
            val = decode_list(val)
        elif type(val) is dict:
            val = decode_dictionary(val)
        elif type(val) is bytes:
            val = val.decode()
        temp[key] = val
    
    d = temp
    return d

def decode_list(l):
    temp = []
    for item in l:
        if type(item) is list:
            temp.append(decode_list(item))
        elif type(item) is dict:
            temp.append(decode_dictionary(item))
        elif type(item) is bytes:
            temp.append(item.decode())
    l = temp
    return l

def decode_torrent(filename):
	f = open(sys.argv[1] , "rb")
	meta = bencodepy.decode(f.read())
	f.close()
	return decode_dictionary(meta) 