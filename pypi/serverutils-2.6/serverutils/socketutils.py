## Made by Frake Namir, sometime in 2020.
## This software program is governed under the terms of the MIT license
## This concludes the license section, and I don't even know why I bothered to add this.

import socket,time


class Data:
    STDCHUNKSIZE=512
## The top socket wrapper for TCP. UDP is crap, and should not be acknowledged as a protocol. (Oh wait, I've never used UDP.)
class TCPSocket:
    '''The bottom-level socket.socket wrapper for Serverutils. It is advised
to use ServerSocket, ClientSocket, and ClientConnection instead,
as they add a nice padding.'''
    def __init__(self,host=None,port=None,blocking=False,sckt=None,recvtries=10):
        self.sckt=sckt or socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sckt.setblocking(blocking)
        self.recvtries=recvtries
        self.host=host
        self.port=port
        self.blocking=blocking
        self.datacapable=True
    def connect(self):
        '''For clients, connect to a URL over TCP'''
        self.sckt.setblocking(True)
        self.sckt.connect((self.host,self.port))
    def bind(self):
        '''For servers, bind to the specified address and port in the object definition'''
        self.sckt.bind((self.host,self.port))
    def listen(self,mxnum=5):
        '''For servers, listen for connections with a default maximum connection cache size of 5'''
        self.sckt.listen(mxnum)
    def accept(self):
        connection, address=self.sckt.accept()
        return TCPSocket(sckt=connection), address
    def serve(self,mxnum=5):
        self.bind()
        self.listen(mxnum)
    def recv(self,numbytes=Data.STDCHUNKSIZE):
        '''Recieve data. Normal recieve size is half a kilobyte, which is a working chunk size for recvall.'''
        if self.datacapable==False: ## Another ridiculous error
            horseradishponieskillingdorkmeggledharbingshubbles(CertainlyNeverGoingToBeARealName)
        data = self.sckt.recv(numbytes) ## Credit to the creator of this file for making a stupid mistake and using self.socket rather than self.sckt.
        if data==b"":
            self.datacapable=False
        return data
    def recvall(self,chunks=Data.STDCHUNKSIZE):
        '''Recieve all possible data, with a chunk size of half a kilobyte, default.'''
        data=bytes()
        self.sckt.setblocking(False)
        tries=0
        try:
            while 1:
                try:
                    p=self.recv(chunks)
                    data+=p
                    if len(p)>0 and len(p)!=Data.STDCHUNKSIZE: ## All the data is recieved!
                        tries=self.recvtries+1
                        raise Exception
                    tries=0 ## If some of the data is recieved successfully, tries=0.
                except:
                    if tries>self.recvtries or data!=b"":
                        raise Exception
                    else:
                        tries+=1
                        time.sleep(0.01)
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
    def sendbytes(self,data): ## Auxilary method.
        self.send(data)
    def close(self):
        self.sckt.shutdown(1)
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
    def recv(self,rcv=Data.STDCHUNKSIZE):
        '''Recieve an amount of data from the client, as a bytes object'''
        return self.socket.recv(rcv)
    def recvtext(self,rcv=Data.STDCHUNKSIZE):
        '''Recieve all data, and return it as a string'''
        return self.recvall(rcv).decode()
    def recvall(self,chunks=Data.STDCHUNKSIZE):
        '''Recieve all available data, and return it as a bytes object.'''
        data=self.socket.recvall(chunks)
        return data
    def sendfile(self,filename):
        '''Send a file.'''
        file=open(filename,"rb")
        self.socket.send(file.read())
        file.close()
    def sendtext(self,data):
        '''Send text data'''
        self.socket.send(data.encode())
    def sendbytes(self,data):
        '''Send bytes data'''
        self.socket.send(data)
    def close(self):
        '''Completely close the socket and end the connection'''
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
