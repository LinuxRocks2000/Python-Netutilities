from .serverlistenable import TCPServer
from .protocols import Protocol_HTTP, HTTPOutgoing, HTTPDATA, HFE
import os


## Remember, Serverutils is EXTENSION ORIENTED!
## All critical components should be replaceable, debuggable, hackable, snackable, etc.
## Thus, leave it to the extensions who can be REMOVED EASIER, EDITED EASIER,
## and allow thrill-seeking coders to FULLY HACK THE SYSTEM!
class HTTPServer(TCPServer): ## Top class for all HTTP-based servers.
    '''An incredibly complex HTTP server base class, not for any
use except maybe creating your own HTTP based servers.'''
    def __init__(self,host,port,blocking=True,**kwargs):
        super().__init__(host,port,blocking,**kwargs)
        self.addProtocol(Protocol_HTTP())
        for x in HTTPDATA.methods: ## For the child classes. Give a top function for every method.
            if hasattr(self,"top"+x):
                self.getHook("http_handle"+x).addTopFunction(self.__getattribute__("top"+x))
        if hasattr(self,"topHTTPFailure"):
            self.getHook("httpfailure").addTopFunction(self.topHTTPFailure)
        self.getHook("init").addFunction(self.initialify)
    def initialify(self):
        self.getHook("http_handle").addEventualFunction(self.send)
        print("Adding sendhook")
    def send(self,incoming,outgoing):
        print("sent")
        outgoing.send() ## Assume that status and other information have already been set.


class SimpleWebServer(HTTPServer):
    def __init__(self,host,port,blocking=True,**kwargs):
        super().__init__(host,port,blocking,**kwargs)
        self.addExtension(JustASimpleWebServerExtension(**kwargs))
