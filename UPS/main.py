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
def recvMsg(socket):
    var_int_buff = []
    while True:
        buf = socket.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = socket.recv(msg_len)
    msg = wu.UConnected()
    msg.ParseFromString(whole_message)
    return msg.result, msg.worldid

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
    
    sendMsg(socket, msgUW);    
    result, worldid = recvMsg(socket)
    if result == "connected!":
        print("New World %d is created!" % worldid)
    else:
        print("Fail to create a new World, %s" % result)

    return result, worldid

# connect to a World
def connectWorld(socket, worldid):
    msgUW = wu.UConnect()
    msgUW.isAmazon = False
    msgUW.worldid = worldid
    
    sendMsg(socket, msgUW);    
    result = recvMsg(socket)
    if result == "connected!":
        print("Connect to World %d!" % worldid)
    else:
        print("Connection to World %d fails, %s" % (worldid, result))

    return result

# main
if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 12345
    socW = buildSocW(HOST, PORT)
    
    res, worldid = createWorld(socW)

    res = connectWorld(socW, worldid)
        
    socW.close()
