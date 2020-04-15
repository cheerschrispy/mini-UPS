import socket

#google protobuf
import world_ups_pb2 as wu
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

HOST = '0.0.0.0'
PORT = 12345

#send a message by socket
def sendMsg(socket, msg):
    msgstr = msg.SerializeToString()
    _EncodeVarint(socket.send, len(msgstr), None)
    s.send(msgstr)
    
#receive a message by socket
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
    return msg

if __name__ == '__main__':
    print('Connecting to World...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    uwMsg = wu.UConnect()
    uwMsg.isAmazon = False
    
    sendMsg(s, uwMsg);    
    data = recvMsg(s)
    print(data)

    s.close()
