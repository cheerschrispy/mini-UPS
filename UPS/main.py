import socket

# google protobuf
import world_ups_pb2 as wu
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

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
    else:
        print("Receive an undefined message.")
        return
    return msg

# build a socket with World
def buildSocW(hostW, portW):
    print('Build a socket to World...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostW, portW))
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
        
    sendMsg(socket, msgUW);    
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


# main
if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 12345
    socW = buildSocW(HOST, PORT)
    
    msg1 = createWorld(socW)
    print(msg1.worldid)
    msg2 = disconnectWorld(socW, msg1.worldid)

    msg3 = connectWorld(socW, msg1.worldid)
    socW.close()
