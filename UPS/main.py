import socket

from tools import *

# google protobuf
import world_ups_pb2 as wu
import AtoU_pb2 as au
import UtoA_pb2 as ua
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

    # connect to Amazon server
    
    hostA = 'vcm-12360.vm.duke.edu'
    portA = 34567
    socA =  buildSoc(hostA, portA)
    

    # create a World and send worldid to Amazon
    msg1 = createWorld(socW)
    sendWorldid(socA, msg1.worldid)
    
    socW.close()
