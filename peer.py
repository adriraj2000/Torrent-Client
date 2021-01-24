import time 
import socket 
import struct
import bitstring
from pubsub import pub
import logging

import message


class Peer(object):
    def __init__(self,number_of_pieces,ip,port = 6881):
        self.last_call = 0.0
        self.healthy = False
        self.read_buffer = b''
        self.has_handshaked = False
        self.socket = None
        self.ip = ip
        self.port = port
        self.number_of_pieces = number_of_pieces
        self.bit_field = bitstring.BitArray(number_of_pieces)
    
    def __hash__(self):
        return "%s:%d" % (self.ip, self.port)
    
    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), timeout=2)
            self.socket.setblocking(False)
            logging.debug("Connected to peer ip: {} - port: {}".format(self.ip, self.port))
            self.healthy = True

        except Exception as e:
            print("Failed to connect to peer (ip: %s - port: %s - %s)" % (self.ip, self.port, e.__str__()))
            return False

        return True
    
    def send_to_peer(self, msg):
        try:
            self.socket.send(msg)
            self.last_call = time.time()
        except Exception as e:
            self.healthy = False
            logging.error("Failed to send to peer : %s" % e.__str__())
    
    