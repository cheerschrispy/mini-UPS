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
def recvWorld(socW, socA, db):
    while True:
        print('wwwwwwwwwwwwwwwwwwwww')
        msg = recvMsg(socW, "UResponses")
        t = threading.Thread(target = UtoA, args = (socW, socA, db, msg))
        t.start()
        t.join()

def recvAmazon(socW, socA, db, worldid):
    while True:
        print('aaaaaaaaaaaaaaaaaaaa')
        msg = recvMsg(socA, "AMessages")
        t = threading.Thread(target = AtoU, args = (socW, socA, db, worldid,msg))
        t.start()
        t.join()
        
###############################################
# main
if __name__ == '__main__':
    # connect to database
    db = connectDB()
    db.cursor().execute("DELETE FROM users_truck;")
    db.cursor().execute("DELETE FROM users_package;")

    # connect to World server
    #hostW = '0.0.0.0'
    hostW = 'vcm-14419.vm.duke.edu'
    #hostW = 'vcm-12360.vm.duke.edu'
    portW = 12345
    socW = buildSoc(hostW, portW)
    
    # create a World
    msg1 = createWorld(socW,db)
    print('Connect with world msg1.worldid!')
    
    # connect to Amazon serve
    #hostA = 'vcm-12360.vm.duke.edu'
    hostA  = 'vcm-14419.vm.duke.edu'
    portA = 34567
    socA =  buildSoc(hostA, portA)
    print('Connect with Aamzon!')

    sendWorldid(socA, msg1.worldid)
    print('sent worldid to Amazon')
    
    threadW = threading.Thread(target = recvWorld, args = (socW, socA, db))
    threadA = threading.Thread(target = recvAmazon, args = (socW, socA, db, msg1.worldid))
    threadW.start()
    threadA.start()
    threadW.join()
    threadA.join()
    


    '''
    msg2 = recvMsg(socA, "AMessages")
    AtoU(socW, socA, db, msg1.worldid, msg2)
    print('received ack for UInitialWorldid')
        
    ####
    msg3 = recvMsg(socA, "AMessages")
    print('received AGetTruck')
    AtoU(socW, socA, db, msg1.worldid, msg3)
    print('replied with ack and sent UGoPickUp')

    msg4 =recvMsg(socW,"UResponses")
    UtoA(socW,socA,db,msg4)
    print("receive ACK from World and completion")


    msg6 =recvMsg(socW,"AMessages")
    AtoU(socW,socA,db, msg1.worldid, msg6)
    print("receive ACK from Amazon")

    print("receive goDeliver from Amazon")
    msg7=recvMsg(socA,"AMessages")
    AtoU(socW, socA, db, msg1.worldid, msg7)
    print("sent goDeliver to world, reply with ack")
    '''





    socW.close()
