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

####################################
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
    
    #send worldid to Amazon
    sendWorldid(socA, msg1.worldid)
    
    socW.close()
