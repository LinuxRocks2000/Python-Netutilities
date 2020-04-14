## A wrapper around the python low-level socket api, made by Tyler Clarke, April 5, 2020.
## Feel free to use and distribute under the terms of any freeware license you care to mention

## When using, just extend the ServerListenable class and define the handle_post and handle_get functions (each with the arguments self, data, and connection).
## And the handle_aux function, if you want to.

## The webserver can be run by creating an object of your extended class, and calling the run function on it.

## Enjoy!

import socket
import json
import mimetypes

class ServerListenable:
    def __init__(self,host="localhost",port=8080,controls=None):
        self.sckt=socket.socket()
        self.sckt.bind((host,port))
        self.inittasks(host,port)
        self.controls=None if not controls else controls(self)
        self.controlsdir="/CONTROLS"
    def run(self):
        self.sckt.listen(5)
        while True:
            self.connection, (client_host, client_port) = self.sckt.accept()
            recieved=self.connection.recv(1024)
            try:
                ppt=self.parseRequest(recieved)
                if ppt["reqtype"]=="POST":
                    if ppt["reqlocation"][0:len(self.controlsdir)]==self.controlsdir and self.controls:
                        self.controls.on_post(ppt,self.connection)
                    else:
                        self.handle_post(ppt,self.connection)
                elif ppt["reqtype"]=="GET":
                    if ppt["reqlocation"][0:len(self.controlsdir)]==self.controlsdir and self.controls:
                        self.controls.on_get(ppt,self.connection)
                        print("On get called")
                    else:
                        self.handle_get(ppt,self.connection)
                else:
                    raise Exception
            except Exception as e:
                self.handle_aux(recieved,self.connection)
            self.connection.close()
    def inittasks(self,host,port):
        pass
    def handle_post(self,data,connection):
        pass
    def handle_get(self,data,connection):
        self.send_file_headers(connection,"text/html")
        connection.send('''
<!DOCTYPE html>

<html>
    <head>
        <title>Web test</title>
    </head>
        <h1>Test page</h1>
        <p>
            This is the first page you see when you create an empty, minimal TCP webserver.<br>
            To get a different page, define the <code>handle_get(self,data,connection)</code> function.<br>
            From <code>handle_get</code>, you can use the send_file function to send a local html file.<br>
            "connection" (third argument) is the socket object connecting to the client, see more about sockets to use this.<br>
            "data" (second argument) is a dict with data on the request, including "reqlocation", which is the location requested by the client.<br>
            "self" (first argument) is an ServerListenable object, see the docs.<br><br>
            This page is incomplete, please see <a href="https://github.com/LinuxRocks2000/netutils">the github repo</a> for more information.
        </p>
    </body>
</html>
'''.encode())
        connection.close()
    def handle_aux(self,req,connection):
        pass
    def send_file_headers(self, connection, typ):
        connection.send("HTTP/1.0 200 OK\n".encode())
        bork = "Content-Type: " + typ + "\n"
        connection.send(bork.encode())
        connection.send("\n".encode())
    def send_file(self,file,connection):
        self.send_file_headers(self,connection,mimetypes.guess_type(file)[0])
        c=open(file)
        connection.send(c.read().encode())
        c.close()
    def parseRequest(self,data):
        toreturn={}
        copy=data.decode()
        copy=copy.replace("\r","")
        toreturn["rawrequesttext"]=str(copy)
        copy=copy.split("\n\n")
        toreturn["content"]=str(copy[1])
        toreturn["rawheaders"]=str(copy[0])
        cop=copy[0].split("\n")
        for x in cop[1:]:
            p=x.split(": ")
            toreturn[p[0]]=p[1]
        top=cop[0].split(" ")
        toreturn["reqtype"]=top[0]
        toreturn["reqlocation"]=top[1]
        toreturn["reqhttpversion"]=top[2]
        return toreturn
