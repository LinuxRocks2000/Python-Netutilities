## Made by Frake Namir, sometime in 2020.
## This software program is governed under the terms of the MIT license
## This concludes the license section, and I don't even know why I bothered to add this.

import socket


class Data:
    STDCHUNKSIZE=512
## The top socket wrapper for TCP. UDP is crap, and should not be acknowledged as a protocol. (Oh wait, I've never used UDP.)
class TCPSocket:
    '''The bottom-level socket.socket wrapper for Serverutils. It is advised
to use ServerSocket, ClientSocket, and ClientConnection instead,
as they add a nice padding.'''
    def __init__(self,host=None,port=None,blocking=False,sckt=None):
        self.sckt=sckt or socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sckt.setblocking(blocking)
        self.host=host
        self.port=port
        self.blocking=blocking
        self.datacapable=True
    def connect(self):
        self.sckt.setblocking(True)
        self.sckt.connect((self.host,self.port))
    def bind(self):
        self.sckt.bind((self.host,self.port))
    def listen(self,mxnum=5):
        self.sckt.listen(mxnum)
    def accept(self):
        connection, address=self.sckt.accept()
        return TCPSocket(sckt=connection), address
    def serve(self,mxnum=5):
        self.bind()
        self.listen(mxnum)
    def recv(self,numbytes=Data.STDCHUNKSIZE):
        '''Recieve data. Normal recieve size is half a kilobyte, which is a working chunk size for recvall.'''
        if self.datacapable==False:
            raise Exception
        data = self.socket.recv(numbytes)
        if data=="":
            self.datacapable=False
        return data
    def recvall(self,chunks=Data.STDCHUNKSIZE):
        '''Recieve all possible data, with a chunk size of half a kilobyte, default.'''
        data=bytes()
        self.sckt.setblocking(False)
        try:
            while 1:
                data+=self.recv(chunks)
                print("In the recvall function (socketutils.py,ln50), the current data is:",data)
        except:
            return data
    def recvtext(self,chunks=Data.STDCHUNKSIZE):
        return self.recvall(chunks).decode()
    def recvfile(self,filename,chunks=Data.STDCHUNKSIZE):
        file=open(filename,"wb+")
        file.write(self.recvall(chunks))
        file.close()
    def send(self,data):
        self.sckt.sendall(data)
    def sendtext(self,data):
        self.sckt.sendall(data.encode())
    def sendfile(self,filename):
        file=open(filename,"rb")
        self.send(file.read())
        file.close()
    def close(self):
        self.sckt.shutdown(1)
        self.sckt.close()
        self.sckt.close()
    def setblocking(self,blocking):
        self.blocking=blocking
        self.sckt.setblocking(blocking)


class ClientConnection:
    '''A connection to the client, returned from ServerSocket's get_connection function.'''
    def __init__(self,sckt,clidata,blocking):
        self.socket=sckt
        self.clidata=clidata
        self.blocking=blocking
    def recieve(self,rcv=Data.STDCHUNKSIZE):
        '''Recieve an amount of data from the client, as a bytes object'''
        return self.socket.recv(rcv)
    def recievetext(self,rcv=Data.STDCHUNKSIZE):
        '''Recieve all data, and return it as a string'''
        return self.recieve(rcv).decode()
    def recieveall(self,chunks=Data.STDCHUNKSIZE):
        '''Recieve all available data, and return it as a bytes object.'''
        data=self.socket.recvall(chunks)
        return data
    def sendfile(self,filename):
        '''Send a file.'''
        file=open(filename,"rb")
        self.socket.sendall(file.read())
        file.close()
    def sendtext(self,data):
        '''Send text data'''
        self.socket.send(data.encode())
    def sendbytes(self,data):
        '''Send bytes data'''
        self.socket.send(data)
    def close(self):
        '''Completely close the socket and end the connection'''
        self.socket.shutdown(1)
        self.socket.close()

class ServerSocket(TCPSocket):
    '''A "server socket", inherited from TCPSocket, which should, through the get_connection function,
return a ClientConnection, another type of socket which contains a TCPSocket and is for easy connections between client and server.'''
    def __init__(self,host,port,mxcons=5,blocking=False):
        super().__init__(host,port,blocking)
        self.serve(mxcons)
    def get_connection(self):
        '''Return a connection, or None if no connection is available and the serversocket is not blocking'''
        try:
            connection,clientdata=self.accept()
            return ClientConnection(connection,clientdata,self.blocking)
        except:
            return None

class ClientSocket(TCPSocket):
    '''The Client counterpart of ServerSocket. Not to be confused with ClientConnection.'''
    def __init__(self,host,port,blocking=False):
        super().__init__(host,port,blocking)
        self.connect()
