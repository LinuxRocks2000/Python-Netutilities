import os


class Protocol:
    def __init__(self,*args,**kwargs):
        self.server=None
        self.inittasks(*args,**kwargs)
    def inittasks(self,*args,**kwargs):
        pass
    def handle(self,*args,**kwargs):
        return True
    def addToServer(self,server):
        self.server=server
        return self.uponAddToServer(server)
    def uponAddToServer(self,server):
        return "NAMELESS"

class HFE: ## HttpFailEvents
    FILENOTFOUND=0
    STRANGEERROR=1
    PERMISSIONDENIED=2
    CLASSIFIED=3 ## The file is found, but classified.


class Protocol_HTTP(Protocol):
    '''The HTTP protocol'''
    def inittasks(self):
        self.clients={}
        self.clnum=0
    def uponAddToServer(self,server):
        self.httprecv=server.addHook("httprecv")
    def connect(self,connection):
        self.clients[self.clnum]=connection
        self.clnum+=1
    def recieve(self,incoming):
        if self.httprecv.doesAnything():
            self.httprecv.call(incoming)
        if hasattr(self.server,"httprecieve"):
            self.server.httprecieve(incoming)
    def run(self):
        for index,element in self.clients.items():
            i=HTTPIncoming(element,self)
            if i.hasMessage:
                self.recieve(i)


class HTTPDATA: ## Static constants for HTTP stuff.
    methods=["GET","POST","HEAD","PUT","DELETE","CONNECT","OPTIONS","TRACE","PATCH"]
    statuspairs={404:"Not Found",400:"Bad Request",500:"Internal Server Error",200:"OK",101:"Switching Protocols",301:"Moved Permanently",401:"Unauthorized",403:"Forbidden",503:"Service Unavailable"}


class HTTPIncoming: ## A "reader" for http requests.
    def __init__(self,socket,http):
        rqstdt={
            "cookies":{},
            "headers":{}
        } ## Data on the request
        rspnsdt={
            "headers":{}
        } ## Data on what will be the response
        continuo=False
        stage=0
        self.socket=socket
        mode=0
        self.http=http
        bufferthingy=""
        cache_headname=""
        cache_cookiename=""
        self.hasMessage=False
        while True:
            if mode==0: ## Read the http request line
                char=""
                try:
                    char=socket.recv(1).decode()
                    self.hasMessage=True
                except:
                    resultcode=400 ## Malformed request.
                    break
                if stage==0: ## Reading the method.
                    if not char==" ":
                        bufferthingy+=char
                    else:
                        stage=1
                        rqstdt["httpmethod"]=bufferthingy ## This is the http method
                        bufferthingy=""
                elif stage==1: ## Reading the uri
                    if not char==" ":
                        bufferthingy+=char
                    else:
                        stage=2
                        rqstdt["uri"]=bufferthingy
                        bufferthingy=""
                elif stage==2: ## Reading the word HTTP, and ignoring it.
                    if char=="/": ## Ignore the word HTTP. Just get the version
                        stage=3
                elif stage==3: ## Reading the version
                    if not char=="\r":
                        bufferthingy+=char
                    else:
                        stage=4
                        rqstdt['version']=bufferthingy
                        bufferthingy=""
                elif stage==4: ## And just a fluffer, to wait until the end of the line.
                    if not char=="\n":
                        rspnsdt["resultcode"]=400 ## Malformed request.
                        break
                    else:
                        mode=1
                        stage=0
            elif mode==1: ## Read all the headers
                char=""
                try:
                    char=socket.recv(1).decode()
                except:
                    resultcode=400 ## Malformed request.
                    break
                if stage==0:
                    if not char in ":\r":
                        bufferthingy+=char
                    elif char=="\r": ## Check stage 3
                        mode=2
                    else:
                        stage=1
                        cache_headname=bufferthingy
                        bufferthingy=""
                elif stage==1:
                    if not char==" ":
                        rspnsdt["resultcode"]=400 ## More malforming
                        break
                    elif cache_headname=="Cookie":
                        mode=4
                        stage=0
                    else:
                        stage=2
                elif stage==2:
                    if not char=="\r":
                        bufferthingy+=char
                    else:
                        if cache_headname=="Cookie":
                            rqstdt["cookies"].append(bufferthingy)
                        else:
                            rqstdt["headers"][cache_headname]=bufferthingy
                        bufferthingy=""
                        stage=3
                elif stage==3:
                    if not char=="\n":
                        rspnsdt["resultcode"]=400 ## More malforming
                        break
                    else:
                        stage=0
            elif mode==2: ## Pass over another line
                char=""
                try:
                    char=socket.recv(1).decode()
                except:
                    resultcode=400 ## Malformed request.
                    break
                if stage==0:
                    if not char=="\n":
                        rspnsdt["resultcode"]=400 ## Malformed request.
                        break
                    else:
                        stage=0
                        mode=3
            elif mode==3: ## Read content, in 8000 bit chunks (1000 octets, bytes, whatever). In test mode it really only reads one at a time, but this code will work with any read number.
                data=""
                if "Content-Length" in rqstdt["headers"]:
                    try:
                        data=socket.recv(int(rqstdt["headers"]["Content-Length"]))
                    except:
                        rspnsdt["resultcode"]=400 ## Malformed request.
                        break
                else:
                    try:
                        while 1:
                            data+=socket.recv(1000).decode()
                    except: pass
                rqstdt["payload"]=data
                break
            elif mode==4: ## Read cookies. Must be entered from the header thingy, and will exit to the header thingy.
                char=""
                try:
                    char=socket.recv(1).decode()
                except:
                    rspnsdt["resultcode"]=400 ## Malformed request.
                    break
                if stage==0:
                    if char=="\r":
                        mode=1
                        stage=3
                    elif char=="=":
                        stage=1
                        cache_cookiename=bufferthingy
                        bufferthingy=""
                    else:
                        bufferthingy+=char
                elif stage==1:
                    if char == ";":
                        stage=0
                        rqstdt["cookies"][cache_cookiename]=bufferthingy
                        bufferthingy=""
                        cache_cookiename=""
                    elif char=="\r":
                        stage=3
                        mode=1
                        rqstdt["cookies"][cache_cookiename]=bufferthingy
                        cache_cookiename=""
                        bufferthingy=""
                    else:
                        bufferthingy+=char
        self.rqstdt=rqstdt
        self.rspnsdt=rspnsdt
    def getOutgoing(self):
        return HTTPOutgoing(self)


class HTTPOutgoing: ## Write counterpart of HTTPIncoming.
    def __init__(self,incoming,status=None,preserveConnection=False):
        self.headers=incoming.rspnsdt["headers"]
        self.http=incoming.http
        self.version=incoming.rqstdt["version"]
        self.filename=None
        self.content=(None if not "content" in incoming.rspnsdt else incoming.rspnsdt["content"])
        self.status=200
        self.incoming=incoming ## Again, simply for further implementation.
        self.connection=incoming.socket
        self.cookies={}
        if "resultcode" in incoming.rspnsdt:
            self.status=incoming.rspnsdt["resultcode"]
    def addHeader(self,headerkey,headervalue):
        self.headers[headerkey]=headervalue
    def addCookie(self,name,value):
        self.cookies[name]=value
    def setContent(self,content):
        self.content=content
    def setFile(self,filename):
        self.filename=filename
    def send(self):
        if self.content:
            self.headers["Content-Length"]=len(self.content)
        elif self.filename:
            self.headers["Content-Length"]=os.path.getsize(self.filename)
        data=("HTTP/"+self.version+" "+str(self.status)+" "+HTTPDATA.statuspairs[self.status]+"\r\n").encode()
        for x,y in self.headers.items():
            data+=(str(x)+": "+str(y)+"\r\n").encode()
        if self.cookies!={}:
            for x,y in self.cookies.items():
                data+=("Set-Cookie: "+x+"="+y+"\r\n").encode()
        data+="\r\n".encode()
        self.connection.sendbytes(data)
        if self.content:
            self.connection.sendtext(self.content)
        elif self.filename:
            self.connection.sendfile(self.filename)
