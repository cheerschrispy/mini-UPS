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

#use list to deal with the ACK
acksOfWorld=[]
worldAckStatus=[]
acksOfAmazon=[]
amazonAckStatus=[]

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
        msg = ua.AMessages()
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
    for i in range(1000):
        truck = msgUW.trucks.add()
        truck.id = i
        truck.x = 100
        truck.y = 100
        addTruck(db, i)
        
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
# send UMessages to Amazon
##Thread: World->Ups->Amazon:Once recv the msg from 
def UtoA(socW, socA, db, msg):
    print('Receive UResponses from World...')

    global seqnumA

    # receive acks from World
    for ack in msg.acks:
        print("The ack from World is ", ack)

    msgUA = ua.UMessages()
    msgUW = wu.UCommands()
    sendUtoW = False
    sendUtoA = False
    
    # receive UFinished from World
    for c in msg.completions:
        sendUtoW = True
        # reply to World with acks
        msgUW.acks.append(c.seqnum)

        # send UtoACommands to Amazon
        # if the truck status is 'arrive warehouse'
        if c.status == 'arrive warehouse':
            sendUtoA = True
            truckReady = msgUA.truckReadies.add()
            truckReady.truckid = c.truckid
            # get whid from database
            truckReady.whid = getWhid(db, c.truckid)
            # update truck status to "arrive warehouse"
            updateTruckStatus(db, c.truckid, "arrive warehouse")
            truckReady.seqnum = seqnumA
            seqnumA += 1 

    # receive UDeliveryMade from World
    for d in msg.delivered:
        sendUtoW = True
        # reply to World with acks
        msgUW.acks.append(d.seqnum)
        # update truck status to "idle"
        updateTruckStatus(db, d.truckid, "idle")
            

    if sendUtoW:
        sendMsg(socW, msgUW)
    if sendUtoA:
        sendMsg(socA, msgUA)
    

#####################################
# receive AMessages from Amazon
# reply with acks 
# send UCommands to World
def AtoU(socW, socA, db, worldid, msg):
    print("Receive Amessages from Amazon...")

    global seqnumW
    global seqnumA

    # receive acks from Amazon
    for ack in msg.acks:
        print("The ack from Amazon is ", ack)

    # prepare UMessages to Amazon
    msgUA = ua.UMessages()
    sendUtoA=False
    
    # receive AInitialWorld from Amazon
    if msg.has_initialWorldid():
        sendUtoA = True
        msgUA.initialWorldid.worldid = worldid
        msgUA.initialWorldid.seqnum = seqnumA
        seqnumA += 1
        
    # reply to Amazon with acks
    for truckCommand in msg.getTrucks:
        sendUtoA = True
        msgUA.acks.append(truckCommand.seqnum)
        ############### DataBase ###############
        #insert new entry in pakage
        


    for deliverCommand in msg.delivers:
        sendUtoA = True
        msgUA.acks.append(deliverCommand.seqnum)

    if sendUtoA:
        sendMsg(socA, msgUA)

    # prepare UCommands to World
    msgUW = wu.UCommands()
    sendUtoW = False
    
    # receive AGetTruck from Amazon
    for truckCommand in msg.getTrucks:
        sendUtoW = True
        goPick = msgUW.pickups.add()
        goPick.truckid = findIdleTruck(db)
        goPick.whid = truckCommand.whid
        # update truck status to "travelling"
        updateTruckStatus(db, gpPick.truckid, "travelling", goPickup.whid)
        goPick.seqnum = seqnumW
        seqnumW += 1
    
    # receive ADeliver from Amazon
    for deliverCommand in msg.delivers:
        sendUtoW = True
        goDeliver = msgUW.deliveries.add()
        goDeliver.truckid = deliverCommand.truckid
        # update truck status to "delivering"
        updateTruckStatus(db, goDeliver.truckid, "delivering")
        goDeliver.seqnum = seqnumW
        seqnumW += 1
        
        # generate a subtype UDeliveryLocation
        for location in deliverCommand.location:
            currLocation = goDeliver.packages.add()
            currLocation.x = location.x
            currLocation.y = location.y
            currLocation.packageid = location.packageid

    if sendUtoW:
        sendMsg(socW, msgUW)
    

    



