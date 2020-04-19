import socket

# google protobuf
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import world_ups_pb2 as wu
import AtoU_pb2 as au
import UtoA_pb2 as ua

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
    elif msgType=="AtoUCommands":
        msg = au.AtoUCommands()
        msg.ParseFromString(whole_message)
    elif msgType=="AtoUResponses":
        msg = ua.AtoUResponses()
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

####################################
# receive UResponses from World
# reply with acks
# send UtoACommands to Amazon
# receive acks from Amazon
def sendUtoA(socW, socA, msg):
    print('Receive UResponses from World...')

    global seqnumW
    global seqnumA

    msgUW = wu.UCommands()
    bool UtoA = False
    msgUA = ua.UtoAResponses()

    for ack in msg.acks:
        print("UCommands[%d] is acked by the World" % ack)
    
    for c in msg.completions:
        # reply to World with acks
        msgUW.acks.append(msg.seqnum)

        # send UtoACommands to Amazon
        # if the truck status is 'arrive warehouse'
        if c.status == 'arrive warehouse':
            UtoA = True
            truckReady = msgUA.truckReadies.add()
            truckReady.truckid = c.truckid
            truckReady.seqnum = seqnumA
            seqnumA += 1

    for d in msg.delivered:
        # reply to World with acks
        msgUW.acks.append(msg.seqnum)

    sendMsg(socW, msgUW)
    if UtoA:
        sendMsg(socA, msgUA)                
        
    return None









#####################################
# receive AtoUCommands from Amazon
# send UtoAResponses to Amazon
# send UCommands to World
#def sendUtoW(socW, socA, msg):
