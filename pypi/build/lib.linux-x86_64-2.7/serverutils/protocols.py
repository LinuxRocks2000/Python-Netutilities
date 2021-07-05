import os
class HFE: ## HttpFailEvents
    FILENOTFOUND=0
    STRANGEERROR=1
    PERMISSIONDENIED=2
    CLASSIFIED=3 ## The file is found, but classified.

class Protocol:
    def __init__(self,*args,**kwargs):
        self.server=None
        self.inittasks(*args,**kwargs)
    def inittasks(self,*args,**kwargs):
        pass
    def handle(self,*args,**kwargs):
        return True
    def addToServer(self,server):
        server.getHook("handle").addTopFunction(self.handle)
        self.server=server
        return self.uponAddToServer(server)
    def uponAddToServer(self,server):
        return "NAMELESS"


class Protocol_HTTP(Protocol):
    '''The HTTP Protocol base class. Never interact directly with the http protocol object.
If necessary, '''
    def inittasks(self):
        self.requests=[]
    def uponAddToServer(self,server): ## The "attachment" function, to add a built protocol to a server.
        server.addHook("httpfailure") ## Primarily for handling on HTTP servers, this program does not touch http failure as of this version. Who cares?
        if hasattr(server,"httpfailed"):
            server.getHook("httpfailure").addFunction(server.httpfailed)
        for x in HTTPDATA.methods:
            hook=server.addHook("http_handle"+x)
            if hasattr(server,"handle"+x.lower()): ## A handler function for every purpose! Twenty percent off!
                hook.addFunction(server.__getattribute__("handle"+x.lower()))
            elif hasattr(self,"handle"+x.lower()):
                hook.addFunction(self.__getattribute__("handle"+x.lower()))
        self.server=server
        p=server.addHook("http_handle")
        p.addFunction(self.http_handle)
        return "HTTP" ## Return the dict name
    def handleget(self,connection,request):
        h=HTTPOutgoing(request)
        h.setStatus(200)
        h.setContent('''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Welcome to serverutils!</title>
</head>
<body>
<h1>Welcome to serverutils!</h1>
<p>If your seeing this, it means you haven't even wrapped the raw Protocol_HTTP. This is a development only page.</p>
</body>
</html>''')
        h.send()
    def http_handle(self,incoming,outgoing):
        self.server.getHook("http_handle"+incoming.type).call(incoming,outgoing)
    def handle(self,connection,data):
        req=None
        try:
            req=HTTPIncoming(connection,data,self)
        except Exception as e:
            return True
        if req.isHTTP:
            try:
                s=self.server.getHook("http_handle")
                s.call(req,req.getOutgoing())
                return False
            except: ## User parse failed. This is mainly for further implementation.
                self.server.getHook("httpfailure").call(req,req.getOutgoing(),HFE.STRANGEERROR)
                return True
        return True
    def getStatusName(self,statuscode):
        return self.statuspairs[statuscode]
    def recieve(self,clientsocket):
        return HTTPIncoming(clientsocket)


class HTTPDATA: ## Static constants for HTTP stuff.
    methods=["GET","POST","HEAD","PUT","DELETE","CONNECT","OPTIONS","TRACE","PATCH"]
    statuspairs={404:"Not Found",400:"Bad Request",500:"Internal Server Error",200:"OK"}


class HTTPIncoming: ## A "reader" for http requests.
    def __init__(self,socket,data,http):
        self.socket=socket
        self.http=http
        self.data=data.decode().replace("\r","")
        contverseheads=self.data.split("\n\n")
        heads=contverseheads[0].split("\n")
        self.headers={}
        for x in heads[1:]:
            hd=x.split(": ")
            self.headers[hd[0]]=hd[1]
        statrow=heads[0].split(" ")
        self.type=statrow[0]
        self.version=statrow[2]
        self.location=statrow[1]
        self.guessErrors=[]
        if len(contverseheads)>1:
            self.extradata=contverseheads[1]
        self.isHTTP=True
        if not self.type in HTTPDATA.methods: ## Cause a ridiculous error.
            self.isHTTP=False
        self.host=self.headers["Host"]
    def getOutgoing(self):
        return HTTPOutgoing(self)


class HTTPOutgoing: ## Write counterpart of HTTPIncoming.
    def __init__(self,incoming,status=None,preserveConnection=False):
        self.headers={}
        self.http=incoming.http
        self.version=incoming.version
        self.filename=None
        self.content=None
        self.status=None
        self.preserve=preserveConnection
        self.incoming=incoming ## Again, simply for further implementation.
        self.connection=incoming.socket
        self.setfile=self.incoming.http.server.addHook("HTTPOutgoing_setFile") ## Security combing for file permissions?
        self.setcontent=self.incoming.http.server.addHook("HTTPOutgoing_setContent") ## You never know.
        self.addheader=self.incoming.http.server.addHook("HTTPOutgoing_addHeader") ## Because this is a pretty open system, security extensions can set top functions on those hooks to prevent unwanted access.
        self.setfile.addFunction(self._setFile)
        self.setcontent.addFunction(self._setContent)
        self.addheader.addFunction(self._addHeader)
    def addHeader(self,headerkey,headervalue):
        self.addheader.call(headerkey,headervalue)
    def _addHeader(self,headerkey,headervalue):
        self.headers[headerkey]=headervalue
    def setContent(self,content):
        self.setcontent.call(content)
    def _setContent(self,content):
        self.content=content
    def setFile(self,filename):
        self.setfile.call(filename)
    def _setFile(self,filename):
        self.filename=filename
    def setStatus(self,newstatus):
        self.status=int(newstatus)
    def setPreserveConnection(self,new):
        self.preserve=new
    def send(self):
        print("Sent!")
        data=(self.version+" "+str(self.status)+" "+HTTPDATA.statuspairs[self.status]+"\r\n").encode()
        for x,y in self.headers.items():
            data+=(x+": "+y+"\r\n").encode()
        data+="\r\n".encode()
        self.connection.sendbytes(data)
        try:
            if self.filename:
                self.connection.sendfile(self.filename)
            elif self.content:
                self.connection.sendtext(self.content)
            if not self.preserve:
                print("Closed connection.")
                self.connection.close()
        except Exception as e:
            print("Whoops, poops.",self.filename,self.incoming.location,e)
            self.incoming.http.server.getHook("httpfailure").call(self.incoming,self,HFE.STRANGEERROR)
