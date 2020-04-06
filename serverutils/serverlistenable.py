## A wrapper around the python low-level socket api, made by Tyler Clarke, April 5, 2020.
## Feel free to use and distribute under the terms of any freeware license you care to mention

## When using, just extend the ServerListenable class and define the handle_post and handle_get functions (each with the arguments self, data, and connection).
## And the handle_aux function, if you want to.

## The webserver can be run by creating an object of your extended class, and calling the run function on it.

## Enjoy!

import socket
import json
class ServerListenable:
    def __init__(self,host,port):
        self.sckt=socket.socket()
        self.sckt.bind((host,port))
    def run(self):
        self.sckt.listen(5)
        while True:
            self.connection, (client_host, client_port) = self.sckt.accept()
            recieved=self.connection.recv(1024)
            try:
                ppt=self.parseRequest(recieved)
                if ppt["reqtype"]=="POST":
                    self.handle_post(ppt,self.connection)
                elif ppt["reqtype"]=="GET":
                    self.handle_get(ppt,self.connection)
                else:
                    raise Exception
            except Exception as e:
                self.handle_aux(recieved,self.connection)
            self.connection.close()
    def handle_post(self,data,connection):
        pass
    def handle_get(self,data,connection):
        pass
    def handle_aux(self,req,connection):
        pass
    def parseRequest(self,data):
        copy=data.decode()
        copy=copy.replace("\r","")
        copy=copy.split("\n")
        toreturn={}
        if copy[0][0:4]=="GET ":
            toreturn["reqtype"]="GET"
        if copy[0][0:4]=="POST":
            toreturn["reqtype"]="POST"
        toreturn["reqlocation"]=copy[0].split(" ")[1]
        toreturn["useragent"]=copy[2].split(" ")[1]
        toreturn["mimetype"]=(copy[3][8:]).split(",")
        toreturn["langtype"]=(copy[4][17:]).split(",")
        if toreturn["reqtype"]=="POST":
            toreturn["data"]=json.loads(copy[13])
        return toreturn
