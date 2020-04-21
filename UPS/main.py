import socket
import threading

from tools import *
from database import *

# google protobuf
import world_ups_pb2 as wu
import ups_amazon_pb2 as ua
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

################################################
def recvWorld(socW, socA):
    while True:
        msg = recvMsg(socW, "UResponses")
        t = threading.Thread(target = UtoA, args = (socW, socA, msg))
        t.start()

def recvAamzon(socW, socA, worldid):
    while True:
        msg = recvMsg(socA, "AMessages")
        t = threading.Thread(target = AtoU, args = (socW, socA, msg, worldid))
        t.start()
        
###############################################
# main
if __name__ == '__main__':
    # connect to World server
    hostW = '0.0.0.0'
    portW = 12345
    socW = buildSoc(hostW, portW)

    # create a World
    msg1 = createWorld(socW)
    
    # connect to Amazon server
    hostA = 'vcm-12360.vm.duke.edu'
    portA = 34567
    socA =  buildSoc(hostA, portA)
    
    threadW = threading.Thread(target = recvWorld, args = (socW, socA))
    threadA = threading.Thread(target = recvAmazon, args = (socW, socA, msg1.worldid))
    threadW.start()
    threadA.start()
    
    socW.close()
