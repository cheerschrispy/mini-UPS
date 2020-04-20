import socket

from database import *

# google protobuf
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import world_ups_pb2 as wu
import ups_amazon_pb2 as ua

#######################################
#sequence number
seqnumW = 0
seqnumA = 0


# send a message by socket
def sendMsg(socket, msg):
    msgstr = msg.SerializeToString()
    _EncodeVarint(socket.send, len(msgstr), None)
    socket.send(msgstr)

# receive a message by socket
def recvMsg(socket, msgType):
    var_int_buff = []
    while True:
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    
    if msgType == "UConnected":
        msg = wu.UConnected()
        msg.ParseFromString(whole_message)
    elif msgType == "UResponses":
        msg = wu.UResponses()
        msg.ParseFromString(whole_message)
    elif msgType=="AMessages":
        msg = au.AtoUCommands()
        msg.ParseFromString(whole_message)
    else:
        print("Receive an undefined message.")
        return
    return msg

# build a socket with World
def buildSoc(host, port):
    print('Build a socket...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

# create a new World
def createWorld(socket):
    msgUW = wu.UConnect()
    msgUW.isAmazon = False
    for i in range(100):
        truck = msgUW.trucks.add()
        truck.id = i
        truck.x = 100
        truck.y = 100

    sendMsg(socket, msgUW)
    msg = recvMsg(socket, "UConnected")
    if msg.result == "connected!":
        print("New World %d is created!" % msg.worldid)
    else:
        print("Fail to create a new World, %s" % msg.result)

    return msg

# connect to a World
def connectWorld(socket, worldid):
    msgUW = wu.UConnect()
    msgUW.isAmazon = False
    msgUW.worldid = worldid

    sendMsg(socket, msgUW)
    msg = recvMsg(socket, "UConnected")
    if msg.result == "connected!":
        print("Connect to World %d!" % msg.worldid)
    else:
        print("Connection to World %d fails, %s" % (msg.worldid, msg.result))

    return msg

# disconnect with a World
def disconnectWorld(socket, worldid):
    msgUW = wu.UCommands()
    msgUW.disconnect = True

    sendMsg(socket, msgUW)
    msg = recvMsg(socket, "UResponses")
    if msg.finished == True:
        print("Disconnect with World %d!" % worldid)
    else:
        print("Disconnection with World %d fails." % worldid)

    return msg

# send worldid to Amazon
def sendWorldid(socket, worldid):
    global seqnumA
    msgUA = ua.UtoACommands()
    msgUA.connectWorld.seqnum = seqnumA
    seqnumA += 1
    msgUA.connectWorld.worldid.append(worldid)
        
    sendMsg(socket, msgUA)




###### May used in mutithread ######
#send back ACK to Amazon
def sendAckToAmazon(socketToAmazon,seqnum):
    msgUA=ua.UtoACommands()
    #use deep copy,covered instead of appended
    msgUA.ack[:]=seqnum
    sendMsg(socketToAmazon,msgUA)

#send back ACK to World
def sendAckToWorld(socketToWorld,seqnum):
    msgUW=wu.UCommands()
    #use deep copy,covered instead of appended
    msgUW.ack[:]=seqnum
    sendMsg(socketToWorld,msgUW)




####################################
# receive UResponses from World
# reply with acks
# send UtoACommands to Amazon
# receive AtoUResponses from Amazon
def UtoA(socW, socA, msg):
    print('Receive UResponses from World...')

    global seqnumA
    
    msgUA = ua.UMessages()
    msgUW = wu.UCommands()

    UtoA = False
    
    for c in msg.completions:
        # reply to World with acks
        msgUW.acks.append(c.seqnum)

        # send UtoACommands to Amazon
        # if the truck status is 'arrive warehouse'
        if c.status == 'arrive warehouse':
            UtoA = True
            truckReady = msgUA.truckReadies.add()
            truckReady.truckid = c.truckid
            truckReady.seqnum = seqnumA
            seqnumA += 1

        #else if c.status="idle"
        #when all the packages are delivered 

    for d in msg.delivered:
        # reply to World with acks
        msgUW.acks.append(d.seqnum)

    sendMsg(socW, msgUW)
    if UtoA:
        sendMsg(socA, msgUA)
    
    return None

#####################################
# receive AtoUCommands from Amazon
# return ACK
# send UtoAResponses to Amazon to send truck 
# send UCommands to World
#def sendUtoW(socW, socA, msg):

def AtoU(socW, socA):
    print("Receive Amessages from Amazon...")

    global seqnumW
    
    # receive the AtoUcommands:getTruck
    msg = recvMsg(socA, "AMessages")
    
    # reply to Amazon with acks
    msgUA = ua.Umessages()
    for truckCommand in msg.getTrucks:
        msgUA.acks.append(truckCommand.seqnum)

    for deliverCommand in msg.delivers:
        msgUA.acks.append(deliverCommand.seqnum)

    sendMsg(socA,msg UA)

    
    msgUW = wu.UCommands()
    # inform World to assign trucks
    for truckCommand in msg.getTrucks:
        goPick = msgUW.pickups.add()
        ###########
        # TODO assign an idle truck (from database?)
        goPick.truckid = seqnumW + 1
        ###########
        goPick.whid = truckCommand.whid
        goPick.seqnum = seqnumW
        seqnumW += 1
    
    # inform World to deliver
    for deliverCommand in msg.delivers:
        goDeliver = msgUW.delivers.add()

        goDeliver.truckid = deliverCommand.truckid
        goDeliver.seqnum = seqnumW
        seqnumW += 1
        
        # generate a subtype UDeliveryLocation
        '''Location = wu.UDeliveryLocation()
        
        Location.packageid = deliverCommand.packageid
        Location.x = deliverCommand.x
        Location.y = deliverCommand.y
        #add it ????????
        Location = goDeliver.packages.add()
'''     
        for location in deliverCommand.packages:
            currLocation = goDeliver.packages.add()
            currLocation.x = location.x
            currLocation.y = location.y
            currLocation.packageid = location.packageid
        

    sendMsg(socW,msgUW)


    #receive the ACK from world
    msgACK = recvMsg(socW,"UResponses")
    #if(seqnumW+1 == msgACK.acks_size):
    #    print("received correct ACK")
    #else:
    print("ACK has ", msgACK.acks_size, " ,seqNum is ", seqnumW)

    

    




