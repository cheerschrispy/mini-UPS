import socket
from database import *
import threading
# google protobuf
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import world_ups_pb2 as wu
import ups_amazon_pb2 as ua

#######################################
#sequence number
seqnumW = 0
seqnumA = 0
mutex = threading.Lock()
#use list to deal with the ACK
acksOfWorld=[]
worldAckStatus=[]
acksOfAmazon=[]
amazonAckStatus=[]

# send a message by socket
def sendMsg(socket, msg):
    print("============")
    print("send:", msg)
    print("============")
   
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
    print("------------")
    print("recv:", msg)
    print("------------")
    
    return msg

# build a socket with World
def buildSoc(host, port):
    print('Build a socket...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

# create a new World
def createWorld(socket,db):
    msgUW = wu.UConnect()
    msgUW.isAmazon = False
    for i in range(10):
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
    # receive AInitialWorld from Amazon
    msg = recvMsg(socket, "AMessages")
    print('received AInitialWorldid from Amazon')
    print("msg: ", msg)    

    msgACK = ua.UMessages()
    msgACK.acks.append(msg.initialWorldid.seqnum)
    sendMsg(socket, msgACK)
    print('replied ack = ', msg.initialWorldid.seqnum)

    msgUA = ua.UMessages()
    msgUA.initialWorldid.worldid.append(worldid)
    msgUA.initialWorldid.seqnum = seqnumA
    with mutex:
        seqnumA += 1
        
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
        if c.status == 'ARRIVE WAREHOUSE':
            print("enter arrive wrhouse if")
            sendUtoA = True
            truckReady = msgUA.truckReadies.add()
            truckReady.truckid = c.truckid
            truckReady.packageid = getPackageIDFromTruckid(db, c.truckid)
            print("find mapping pckid is :",truckReady.packageid )

            # update truck status to "arrive warehouse"
            updateTruckStatus(db, c.truckid, "arrive warehouse")
            truckReady.seqnum = seqnumA
            mutex=threading.Lock()
            with mutex:
                seqnumA += 1 
            ############### Packages Database ###############
            #update the current package status
            pckid = getPackageIDFromTruckid(db, c.truckid)    
            updatePackageStatus(db, "packing", pckid)          
            
    # receive UDeliveryMade from World
    for d in msg.delivered:
        sendUtoW = True
        # reply to World with acks
        msgUW.acks.append(d.seqnum)
        # update truck status to "idle"
        updateTruckStatus(db, d.truckid, "idle")
        ############### Packages Database ###############
        updatePackageStatus(db,"delivered",d.packageid)

            

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

    ##-----------Deal with ms from A----------
    # prepare UMessages to Amazon
    msgUA = ua.UMessages()
    sendUtoA=False
        
    # reply to Amazon with acks
    for truckCommand in msg.getTrucks:
        print('2222')
        sendUtoA = True
        msgUA.acks.append(truckCommand.seqnum)

    for deliverCommand in msg.delivers:
        print('3333')
        sendUtoA = True
        msgUA.acks.append(deliverCommand.seqnum)

    if sendUtoA:
        print('4444')
        sendMsg(socA, msgUA)


    # prepare UCommands to World
    msgUW = wu.UCommands()
    
    # receive AGetTruck from Amazon
    hasGetTrucks = False
    for truckCommand in msg.getTrucks:
        hasGetTrucks = True
        print('6666')
        goPick = msgUW.pickups.add()
        goPick.truckid = findIdleTruck(db)
        goPick.whid = truckCommand.whid
        ############### Truck Database ###############
        # update truck status to "travelling"
        updateTruckStatus(db, goPick.truckid, "travelling", truckCommand.whid)
        goPick.seqnum = seqnumW
        with mutex:
            seqnumW += 1
            ############### Packages Database ###############
            #make details in each packages
        detail="yige"
        for product in truckCommand.product:
            #info=product.count+" X "+product.description+" ,productID is "+product.productid+"\n"
            info=product.description
            detail+=info
            #insert new entry in pakage
        if(truckCommand.uAccountName != ""):
            print(truckCommand.uAccountName)
            msgUA = ua.UMessages()
            msgUA.accountResult.packageid = truckCommand.packageid
            msgUA.accountResult.uAccountExists = validateUserName(db, truckCommand.uAccountName)
            msgUA.accountResult.uAccountName = truckCommand.uAccountName
            msgUA.accountResult.uAccountid = 0
            msgUA.accountResult.seqnum = seqnumA
            with mutex:
                seqnumA += 1
            sendMsg(socA, msgUA)

            #print(detail,truckCommand.packageid,truckCommand.whid,truckCommand.uAccountName,truckCommand.x,truckCommand.y)
            addPackage(db,detail,truckCommand.packageid,goPick.truckid,truckCommand.uAccountName,truckCommand.x,truckCommand.y)
        else:
            addPackage(db,detail,truckCommand.packageid,goPick.truckid,"",truckCommand.x,truckCommand.y)

    if hasGetTrucks:
        sendMsg(socW, msgUW)
        ############### Packages Database ###############
        #TODO: if receive ACK from world.(gettruck),should change status to on-way

        pckid=getPackageIDFromTruckid(db,goPick.truckid)
        #for p in pckid:
        print("the updating truck is:",pckid)
        updatePackageStatus(db,'truck enroute to wharehouse',pckid)
        


    
    # receive ADeliver from Amazon
    ##### TODO
    hasDeliver=False
    for deliverCommand in msg.delivers:
        hasDeliver=True
        goDeliver = msgUW.deliveries.add()
        goDeliver.truckid = deliverCommand.truckid
        # update truck status to "delivering"
        updateTruckStatus(db, goDeliver.truckid, "delivering")
        goDeliver.seqnum = seqnumW
        with mutex:
            seqnumW += 1
            
        # generate a subtype UDeliveryLocation
        #for location in deliverCommand.location:
        currLocation = goDeliver.packages.add()
        ############### Packages Database ###############
        #need to use x, y in database
        currLocation.packageid = getPackageIDFromTruckid(db,goDeliver.truckid)
        xy=getXY(db,currLocation.packageid)
        currLocation.x=xy[0]
        currLocation.y=xy[1]
        
            ############### Packages Database ###############
        pckid=getPackageIDFromTruckid(db,deliverCommand.truckid)
        updatePackageStatus(db,"out for deliver",pckid)
    if hasDeliver:
        sendMsg(socW, msgUW)
    ############### Packages Database ###############
    ##TODO：if receive the world's ACK, update to"out for deliver"


    
    

    



