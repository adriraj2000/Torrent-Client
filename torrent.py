
import sys
import logging
import os
import bencodepy
import decoding
import hashlib
import string
import random
from threading import *
import requests

# general torrent settings
torrent_settings = {
    "max_d_speed": 0,
    "max_u_speed": 0,
    "pieces_downloaded": 0,
    "download_location": os.getcwd()+"/",
    "upload_location": ""
}

if(len(sys.argv) < 2):
    print("Invalid arguments")
    sys.exit(1)
else:
    if(not os.path.isfile(sys.argv[1])):
        raise Exception()
    try:
        for i in range(2, len(sys.argv), 2):
            if(sys.argv[i] == '-d'):
                print(int(sys.argv[i+1]))
                torrent_settings['max_d_speed'] = int(sys.argv[i+1])
            if(sys.argv[i] == '-l'):
                if(os.path.isdir(sys.argv[i+1])):
                    torrent_settings["download_location"] = sys.argv[i+1] + "/"
                else:
                    raise Exception()
    except Exception as e:
        logging.exception(e)
        print("Invalid args")
        sys.exit(1)

# Decoding the bencoded torrent file and extracting the metadata
f = open(sys.argv[1], "rb")  # Read in buffer mode
data = bencodepy.decode(f.read())

metadata = {}
for key, val in data.items():
    metadata[key.decode()] = val

final_metadata = decoding.decode_torrent(sys.argv[1])
info_hash = hashlib.sha1(bencodepy.encode(metadata['info'])).digest()


PORT_NO = 6881
# random generated peer id for this client
PEER_ID = ''.join(random.choices(string.digits, k=20))

torrent_params = {
    "info_hash": info_hash,
    "peer_id": PEER_ID,
    "uploaded": 0,
    "downloaded": 0,
    "left": final_metadata['info']['length'],
    "port": PORT_NO
}

# We will be sorting pieces according to their availabilty
rarest_pieces = []

# We will be keeping track of all the information related to received pieces
received_pieces = [{"index": i, "done": False, "downloading": False, "begin": 0,
                    "downloading_peer": None, "count": 0} for i in range(len(final_metadata['info']['pieces']))]

# This will store the peers obtained from tracker
peers = []

# Opening torrent file.
try:
    downloading_file = open(
        torrent_params['download_location'] + final_metadata['info']['name'], "rb+")
except:
    create = open(torrent_params['download_location'] +
                  final_metadata['info']['name'], "w")
    create.close()
    downloading_file = open(
        torrent_params['download_location']+final_metadata['info']['name'], "rb+")


rarest_piece_lock = Lock()  # lock for rarest piece list
peer_lock = Lock()  # lock for peers list
received_pieces_lock = Lock()

# All the tracker related code here and parsing the messages and the communication
# between the peers


def write_piece(index, begin, block):
    downloading_file.seek(
        (index * final_metadata['info']['piece length'])+begin, 0)
    downloading_file.write(block)


def read_piece(index):
    downloading_file.seek((index * metadata['info']['piece length']), 0)

    if(index == len(metadata['info']['pieces'])-1):
        piece = downloading_file.read(
            metadata['info']['length'] - (index * metadata['info']['piece length']))
    else:
        piece = downloading_file.read(metadata['info']['piece length'])
    return piece
