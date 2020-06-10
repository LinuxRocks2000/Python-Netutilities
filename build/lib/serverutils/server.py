from .serverlistenable import TCPServer
from .protocols import Protocol_HTTP, HTTPOutgoing


class HTTPServer(TCPServer):
    def __init__(self,host,port,blocking=True,httpguess=True,errpages={}):
        super().__init__(host,port,blocking)
        self.addProtocol(Protocol_HTTP(httpguess))
    def httpfailed(self,req):
        p=req.getOutgoing()
        p.setStatus(200)
        p.send()
h=HTTPServer("",8080)
