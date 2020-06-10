from .serverlistenable import TCPServer
from .protocols import Protocol_HTTP, HTTPOutgoing, HTTPDATA, HFE
import os


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
        self.inittasks(**kwargs)
class SimpleHTTPServer(HTTPServer):
    '''A simple child of HTTPServer. Mainly designed as
a base class for more functional servers.
If need be, you can use this one. Just don't forget to override the get404 function,
which should return an HTML 404 page.'''
    def inittasks(self,sitedir=""):
        sitedir=sitedir or "."
        self.sitedir=sitedir+"/" if sitedir[-1]!="/" else sitedir
        if "HTTP" in self.protocols: ## Because of the... Er.. Bad parenting, this function will run twice, once with HTTP support and once without. (Because of the super init tree).
            self.getHook("http_handle").addTopFunction(self.filter_reqloc,0)
            print("Init With HTTP")
    def filter_reqloc(self,incoming,outgoing):
        '''Sterilize the location of the request. Do not touch unless you know what your doing.'''
        realpos=incoming.location
        if realpos[0]=="/":
            realpos=realpos[1:]
        realpos=self.sitedir+realpos
        realpos=realpos.replace("/../","/") ## Make sure unsavory characters can't hack you out by sending get requests with ../ as the location
        incoming.location=os.path.abspath(realpos+("index.html" if incoming.location[-1]=="/" else "")) ## All later tasks will also use this new safe version. Turns urls like "../../../important.fileextension to ./important.fileextension, obviously not as damaging unless you made an important document public.
        return True ## Don't ever forget return in a top function.
    def topGET(self,incoming,outgoing):
        print("Get Request Recieved")
        if os.path.exists(incoming.location):
            if os.path.isfile(incoming.location):
                outgoing.setFile(incoming.location)
                outgoing.setStatus(200)
                outgoing.send()
            else:
                outgoing.setFile(incoming.location)
                outgoing.setStatus(200)
                outgoing.send()
            return True
        else:
            self.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND)
        return False
    def topHTTPFailure(self,incoming,outgoing,event): ## Event should be what happened. "FILENOTFOUND", thus, would be a 404, essentially
        if event==HFE.FILENOTFOUND:
            outgoing.setStatus(404)
            outgoing.setContent(self.get404())
            outgoing.send()
    def get404(self):
        return '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>404 Not Found</title>
</head>
<body>
<h1>To make it clear, <strong>404 NOT FOUND!</strong></h1>
</body>
</html>'''
