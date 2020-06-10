class Protocol_HTTP:
    '''The HTTP Protocol base class. Never interact directly with the http protocol object.
If necessary, '''
    def __init__(self, guess=False, errpages={}):
        errs={404:HTTPDATA.Errpage_404,500:HTTPDATA.Errpage_500}
        self.errpages={}
        for x in errs:
            if x in errpages:
                self.errpages[x]=errpages[x]
                continue
            self.errpages[x]=errs[x]
        self.requests=[]
        self.server=None
        self.guess=guess
    def addToServer(self,server): ## The "attachment" function, to add a built protocol to a server.
        server.getHook("handle").addTopFunction(self.handle)
        server.addHook("httpfailure")
        if hasattr(server,"httpfailed"):
            server.getHook("httpfailure").addFunction(server.httpfailed)
        for x in HTTPDATA.methods:
            hook=server.addHook("http_handle"+x)
            if hasattr(server,"handle"+x.lower()): ## A handler function for every purpose! Twenty percent off!
                hook.addFunction(server.__getattribute__("handle"+x.lower()))
            elif hasattr(self,"handle"+x.lower()):
                hook.addFunction(self.__getattribute__("handle"+x.lower()))
        self.server=server
    def handleget(self,connection,request):
        h=HTTPOutgoing(request)
        h.setStatus(200)
        h.send()
    def handle(self,connection,data):
        print("Request handle in protocols.py handle (line 31) begins...")
        print(data)
        req=None
        try:
            req=HTTPIncoming(connection,data,self.server,self.guess)
        except:
            print("Request generate failure...")
            return True
        if req.isHTTP:
            try:
                self.server.getHook("http_handle"+req.type).call(req)
                print("Request is HTTP, and the http handlehook was called successfully.")
                return False
            except: ## Malformed request. This is mainly for further implementation.
                self.server.getHook("httpfailure").call(req)
                print("Request is HTTP, but the http handlehook failed indicating a malformed request.")
                return True
        print("Request is not HTTP.")
        return True
    def getStatusName(self,statuscode):
        return self.statuspairs[statuscode]
    def recieve(self,clientsocket):
        return HTTPIncoming(clientsocket)


class HTTPDATA: ## Static constants for HTTP stuff.
        methods=["GET","POST","HEAD","PUT","DELETE","CONNECT","OPTIONS","TRACE","PATCH"]
        statuspairs={404:"Not Found",400:"Bad Request",500:"Internal Server Error",200:"OK"}
        templateget='''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>The standard Serverutils HTTP page</title>
</head>
<body>
<h1>Welcome to serverutils! This page is a hard-coded landing page for Serverutils HTTP.</h1>
<p>You are seeing this because you did not override the handle_get function in your server, or you are using an improperly configured server.<br>
In order to get a different page, create an HTML file and use the response.sendFile function.<br>
(Or just write the HTML inline. The beauty of serverutils is that it doesn't give a crap about where the data comes from.)
</p>
</body>
</html>'''
        Errpage_404='''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>The standard Serverutils HTTP page</title>
</head>
<body>
<h1>Welcome to serverutils! This page is the automatic 404 page for Serverutils.</h1>
<p>You are seeing this because you did not define the errpages named argument in the HTTP protocol object. <br>
If you didn't use the HTTP protocol object, then something is seriously wrong with the server you used.<br>
In order to get a different page, use a different server with a better automatic 404, or make a 404.html file.
(Or just write the HTML inline. The beauty of serverutils is that it doesn't give a crap about where the data comes from.)
</p>
</body>
</html>'''
        Errpage_500='''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>The standard Serverutils HTTP page</title>
</head>
<body>
INTERNAL SERVER BEEP BOOPER ERRORER</p>
</body>
</html>'''


class HTTPIncoming: ## A "reader" for http requests.
    def __init__(self,socket,data,server,guess=False):
        try:
            self.socket=socket
            self.server=server
            self.guess=guess
            self.data=data.replace("\r","")
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
            self.isHTTP=True
            if not self.type in HTTPDATA.methods: ## Cause a ridiculous error.
                expertsagreethatthiswillneverbeaname(hokeypokeyisabrokey)
            self.host=self.headers["Host"]
        except:
            self.isHTTP=False
    def getOutgoing(self):
        return HTTPOutgoing(self,guess=self.guess)


class HTTPOutgoing: ## Write counterpart of HTTPIncoming.
    def __init__(self,incoming,status=None,guess=True):
        self.headers={}
        self.server=incoming.server
        self.version=incoming.version
        self.filename=None
        self.content=None
        self.guess=guess
        self.status=None
        self.incoming=incoming ## Again, simply for further implementation.
        self.connection=incoming.socket
    def addHeader(self,headerkey,headervalue):
        self.headers[headerkey]=headervalue
    def setContent(self,content):
        self.content=content
    def setFile(self,filename):
        self.filename=filename
    def setStatus(self,newstatus):
        self.status=int(newstatus)
        if self.guess:
            if self.status==404:
                h=self.server.getHook("httpfailure")
                if h.doesAnything():
                    h.call(self,404)
                else:
                    self.content=HTTPData.Errpage_404
            if self.status==500:
                h=self.server.getHook("httpfailure")
                if h.doesAnything():
                    h.call(self,500)
                else:
                    self.content=HTTPData.Errpage_500
    def send(self):
        data=(self.version+" "+self.status+" "+HTTPData.statuspairs[self.status]+"\r\n").encode()
        for x,y in self.headers.items():
            data+=(x+": "+y+"\r\n").encode()
        data+="\r\n".encode()
        self.connection.sendbytes(data)
        if self.guess and self.status==404:
            self.connection.sendtext(HTTPDATA.Errpage_404)
        try:
            if self.filename:
                self.connection.sendfile(self.filename)
            elif self.content:
                self.connection.sendtext(self.content)
            elif self.guess and self.status==200:
                self.setContent(HTTPDATA.templateget)
                self.send()
        except FileNotFoundError:
            if self.guess:
                self.setStatus(404)
                self.send()
        except:
            if self.guess:
                self.setStatus(500)
                self.send()
