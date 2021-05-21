
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
import json
import socket
from struct import *
from urllib.parse import parse, urlparse

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
met = bencodepy.decode(f.read())
meta = {}
for key, val in met.items():
    meta[key.decode()] = val

metadata = decoding.decode_torrent(sys.argv[1])

# "announce":"udp://tracker.coppersurfer.tk:6969/announce",
#    "created by":"uTorrent/1870",
#    "creation date":1462355939,
#    "encoding":"UTF-8",
#    "info":{
#       "length":124234,
#       "name":"puppy.jpg",
#       "piece length":16384,
#       "pieces":"T�k�/�_(�S\\u0011h%���+]q\\'B\\u0018�٠:����p\\"�j����1-g\\"\\u0018�s(\\u001b\\u000f���V��=�h�m\\u0017a�nF�2���N\\r�ǩ�_�\\u001e\\"2���\"'�wO���-;\\u0004ע\\u0017�ؑ��L&����0\\u001f�D_9��\\t\\\\��O�h,n\\u001a5g�(��仑,�\\\\߰�%��U��\\u0019��C\\u0007>��df��\"}}"

info_hash = hashlib.sha1(bencodepy.encode(meta['info'])).digest()


PORT_NO = 6881
# random generated peer id for this client
PEER_ID = ''.join(random.choices(string.digits, k=20))


torrent_params = {
    "info_hash": info_hash,
    "peer_id": PEER_ID,
    "uploaded": 0,
    "downloaded": 0,
    "left": metadata['info'][b'length'],
    "port": PORT_NO
}

# We will be sorting pieces according to their availabilty
rarest_pieces = []

# We will be keeping track of all the information related to received pieces
received_pieces = [{"index": i, "done": False, "downloading": False, "begin": 0,
                    "downloading_peer": None, "count": 0} for i in range(len(metadata['info'][b'pieces']))]

# This will store the peers obtained from tracker
peers = []


# Opening torrent file.
try:
    downloading_file = open(
        torrent_settings['download_location'] + metadata['info'][b'name'].decode('UTF-8'), "rb+")
except:
    create = open(torrent_settings['download_location'] +
                  metadata['info'][b'name'].decode('UTF-8'), "w")
    create.close()
    downloading_file = open(
        torrent_settings['download_location']+metadata['info'][b'name'].decode('UTF-8'), "rb+")


rarest_piece_lock = Lock()  # lock for rarest piece list
peer_lock = Lock()  # lock for peers list
received_pieces_lock = Lock()

# -----------------------------------------------------


def http_tracker(url, par):
    global peers
    try:
        response = requests.get(url, params=par, timeout=10)
        if(response):
            temp, peer_data = {}, bencodepy.decode(response.content)

            for key, val in peer_data.items():
                temp[key.decode()] = val

            peer_data = temp
            for peer in peer_data['peers']:
                temp = {}
                for key, val in peer.items():
                    temp[key.decode()] = val
                temp['ip'] = temp['ip'].decode()
                peer_lock.acquire()
                peers.append(temp)
                peer_lock.release()
    except Exception as e:
        print("Error reaching http tracker", url)
        return None


def udp_tracker(domain, port, params):  # http://www.bittorrent.org/beps/bep_0015.html
    global peers
    '''Connection Request and Response'''
    protocol_id = 0x41727101980
    action = 0  # connection
    transaction_id = random.randrange(0, 2147483647)

    # All values are send in network byte order (big endian)
    data = pack('!qii', protocol_id, action, transaction_id)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    try:
        sock.sendto(data, (domain, int(port)))
    except Exception as e:
        print("Could not connect to tracker", domain, port)
        return None
    try:
        data, server = sock.recvfrom(1024)
        action, transaction_id, connection_id = unpack('!iiq', data)
    except Exception as e:
        print("No response")
        return None

    '''Announce Request and Response'''
    action = 1  # announce
    event, ip_address, key, num_want = 0, 0, random.randrange(
        0, 2147483647), -1
    data = pack('!qii20s20sqqqiiiih', connection_id, action, transaction_id, params['info_hash'], params['peer_id'].encode(
    ), params['downloaded'], params['left'], params['uploaded'], event, ip_address, key, num_want, params['port'])

    try:
        sock.sendto(data, (domain, int(port)))

    except Exception as e:
        print("Could not connect to tracker", domain, port)
        return None

    try:
        data, server = sock.recvfrom(1024)
        if(len(data) >= 20):
            action, transaction_id_tmp, inteval, leechers, seeders = unpack(
                '!iiiii', data[:20])
            n = int((len(data)-20) / 6)
            res = unpack("!"+n*'BBBBH', data[20:])
            peer_lock.acquire()
            for x in range(0, len(res), 5):
                i1, i2, i3, i4, port = res[x:x+5]
                ip = str(i1)+"."+str(i2)+"."+str(i3)+"."+str(i4)
                peers.append({'ip': ip, 'port': port})
            peer_lock.release()

    except Exception as e:
        print("No response for announce")
        return None


def get_all_peers(metadata, params):
    url_p = urlparse(metadata['announce'])
    global peers
    http_threads = []
    udp_threads = []
    if(url_p.scheme == 'http' or url_p.scheme == 'https'):
        # http_tracker(metadata['announce'],par)
        http_threads.append(
            Thread(target=http_tracker, args=(metadata['announce'], params)))

    elif(url_p.scheme == 'udp'):
        domain, port = url_p.netloc.split(":")
        # udp_tracker(domain,port,par)
        udp_threads.append(
            Thread(target=udp_tracker, args=(domain, port, params)))

    for tracker in metadata['announce-list']:
        url_p = urlparse(tracker[0])
        if(url_p.scheme == 'udp'):
            domain, port = url_p.netloc.split(":")
            # udp_tracker(domain,port,par)
            udp_threads.append(
                Thread(target=udp_tracker, args=(domain, port, params)))

        elif(url_p.scheme == 'https' or url_p.scheme == 'http'):
            #http_tracker(tracker[0], par)
            http_threads.append(
                Thread(target=http_tracker, args=(tracker[0], params)))

    for h in http_threads:
        h.start()
    for u in udp_threads:
        u.start()
    for h in http_threads:
        h.join()
    for u in udp_threads:
        u.join()
    temp = []
    for peer in peers:
        if peer not in temp: # Won't be making repetitive calls
            temp.append(peer)
    peers = temp


def write_piece(index, begin, block):
    downloading_file.seek(
        (index * metadata['info'][b'piece length'])+begin, 0)
    downloading_file.write(block)


def read_piece(index):
    downloading_file.seek((index * metadata['info'][b'piece length']), 0)

    if(index == len(metadata['info'][b'pieces'])-1):
        piece = downloading_file.read(
            metadata['info'][b'length'] - (index * metadata['info'][b'piece length']))
    else:
        piece = downloading_file.read(metadata['info'][b'piece length'])
    return piece
