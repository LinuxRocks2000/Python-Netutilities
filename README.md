A python module for simplifying the programming of specialized TCP servers

Written in pure python, netutils (serverutils) is designed on an object-oriented basis and interacts directly with the underlying socket api for python, allowing the programmer to control everything from http headers to encryption protocols to special requests

A simple serverutils echo server would look something like this:

```python
from serverutils import ServerListenable ## Extend the class ServerListenable to write servers

class MyServer:
    def handle_get(self,data,connection): ## Handle get is called when a get request is sent. Data is a dict containing some parsed header information, as well as the headers themselves.
        connection.send(data["rawrequesttext"].encode()) ## Connection is a python socket object, the one with a connection to the client
        connection.close() ## This helps with the errors
    def handle_post(self,data,connection):
        connection.send(data["rawrequesttext"].encode()) ## Post requests will also be echoed
        connection.close()
    def handle_aux(self,recieved,connection):
        connection.send(recieved) ## Called as kind of a fallback. Any errors in the calling of the above will trigger this one.
        connection.close() ## Its the only appropriate one for an echo server.

m=MyServer("",80) ## Empty string as the first argument (the hostname) allows the computer to be connected to from any associable address (so localhost, the computers name, the computers ip address)
m.run() ## Begin the socket server
        
```
And this should run as a working echo server!
(However, you need root/admin to use port 80. It is recommended to change the port number)
