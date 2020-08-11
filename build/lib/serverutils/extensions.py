import json
import os
import sys
from .protocols import HFE, HTTPDATA, HTTPOutgoing
import imp
import gzip, shutil
import traceback


class Extension:
    '''Base class for all extensions. Override inittasks and uponAddToServer. Remember,
uponAddToServer MUST return the name of the extension, for later use obviously.'''
    def __init__(self,*args,**kwargs):
        self.server=None
        self.inittasks(*args,**kwargs)
    def inittasks(self):
        pass
    def addToServer(self,server,*args,**kwargs):
        self.server=server
        return self.uponAddToServer(*args,**kwargs)
    def uponAddToServer(self):
        pass


class PyHP(Extension):
    def inittasks(self,config={}):
        self.config={"index":"index.pyhp"}
        self.config.update(config)
    def uponAddToServer(self):
        self.server.getHook("httprecv").addFunction(self.handle)
        return "pyhp" ## Extensions should always return a name
    def handle(self,incoming):
        try:
            locale=incoming.rqstdt["uri"]
            if locale.endswith(".pyhp"):
                i=imp.load_source("Imported",locale)
                if hasattr(i,"handle"+incoming.rqstdt["httpmethod"].lower()):
                    data=i.__getattribute__("handle"+incoming.rqstdt["httpmethod"].lower())(incoming,self.server) ## Should return a tuple with the first element being the event status code, and the second element being the content
                    incoming.rspnsdt["resultcode"]=data[0]
                    incoming.rspnsdt["content"]=data[1]
        except Exception as e:
            traceback.print_exc()


class SimpleGzipper(Extension):
    '''Simple GZIP-encoding extension for sending large
files. Stores the gzipped files in a cache.'''
    def uponAddToServer(self,cachelocale=".serverutils-gzipper-cache/"):
        self.cachelocale=cachelocale
        if not os.path.exists(cachelocale):
            os.mkdir(cachelocale)
        if not os.path.exists(cachelocale+"md5caches"):
            p=open(cachelocale+"md5caches","w+")
            p.close()
        self.server.getHook("httprecv").addFunction(self.handle)
        return "SimpleGzipper"
    def isCacheInvalid(self,filename):
        data=self.openCache()
        crmtime=os.path.getmtime(filename)
        if (not filename in data) or (crmtime!=data[filename]):
            return True
        return False
    def validateCache(self,filename):
        d=self.openCache()
        d[filename]=str(os.path.getmtime(filename))
        self.writeCache(d)
    def writeCache(self,ncache):
        file=open(self.cachelocale+"md5caches","w")
        data=""
        for x,y in ncache.items():
            data+=str(x)+" : "+str(y)+"\n"
        file.write(data)
        file.close()
    def openCache(self):
        file=open(self.cachelocale+"md5caches")
        data=file.read()
        file.close()
        d=data.split("\n")[:-1] ## Use all but the last, unfilled, line.
        returner={}
        for x in d:
            ps=x.split(" : ")
            returner[ps[0]]=float(ps[1])
        return returner
    def handle(self,incoming):
        ## Only do any of this if outgoing has a file send
        try:
            if os.path.isfile(incoming.rqstdt["uri"]) and not (incoming.rqstdt["uri"].endswith(".pyhp") and "pyhp" in self.server.extensions) and "Accept-Encoding" in incoming.rqstdt["headers"] and "gzip" in incoming.rqstdt["headers"]["Accept-Encoding"]:
                location=incoming.rqstdt["uri"].replace("/",".")
                print("Doing actual handling in gzipper")
                print("BTW, the current URI is",incoming.rqstdt["uri"])
                if self.isCacheInvalid(incoming.rqstdt["uri"]):
                    self.validateCache(incoming.rqstdt["uri"])
                    file=open(incoming.rqstdt["uri"],"rb")
                    gzipped=gzip.open(self.cachelocale+'"'+location+'.gz"',"wb")
                    shutil.copyfileobj(file,gzipped)
                    file.close()
                    gzipped.close()
                incoming.rqstdt["uri"]=self.cachelocale+'"'+location+'.gz"'
                incoming.rspnsdt["headers"]["Content-Encoding"]="gzip"
        except:
            traceback.print_exc()


class IncrediblySimpleWebSend(Extension):
    def inittasks(self,config=None):
        self.config={
            "404":["inline","404 not found. For better 404 messages, add a config dictionary to your IncrediblySimpleWebSend object and set the 404 to a list like this: ['inline','Your inline 404 here'], or this: ['file','your 404 file name here']"],
            "sitedir":"pages",
            "index":"index.html"}
        self.config.update(config)
    def uponAddToServer(self): ## Compatible with Protocol_HTTP
        self.server.getHook("httprecv").addEventualFunction(self.httprecv)
        return "IS-Websend"
    def httprecv(self,incoming):
        if incoming.rqstdt["httpmethod"]=="GET":
            print("Will send")
            try:
                o=HTTPOutgoing(incoming)
                if os.path.isfile(incoming.rqstdt["uri"]):
                    o.setFile(incoming.rqstdt["uri"])
                else:
                    if self.config["404"][0]=="inline":
                        o.setContent(self.config["404"][1])
                    elif self.config["404"][0]=="file":
                        o.setFile(self.config["404"][1])
                    o.status=404 ## Not a file.
                o.send()
            except:
                traceback.print_exc()
            print("Sent!")


class URISterilizer(Extension):
    def inittasks(self,config={}):
        self.config={"relativepaths":True,"noparentdir":True,"primeforwebsend":True,"useindexindirectory":True,"completehtmlfileextension":True,"primeforpyhp":True}
        self.config.update(config)
    def uponAddToServer(self):
        self.server.getHook("httprecv").addFunction(self.httprecv)
        return "URISterilizer"
    def httprecv(self,incoming):
        uri=incoming.rqstdt["uri"]
        if self.config["relativepaths"]==True and uri[0]=="/": uri=uri[1:]
        if self.config["noparentdir"]==True and "../" in uri: uri.replace("../","")
        if self.config["primeforwebsend"]==True: ## Designed for compatibility with the WebSend family of HTTP server senders
            if "IS-Websend" in self.server.extensions: ## Incredibly Simple WebSend
                websconfig=self.server.extensions["IS-Websend"].config
                uri=websconfig["sitedir"]+("/" if not websconfig["sitedir"][-1]=="/" else "")+uri
                if self.config["useindexindirectory"]==True and os.path.isfile(uri+("/" if not uri[-1]=="/" else "")+websconfig["index"]):
                    uri+=("/" if not uri[-1]=="/" else "")+websconfig["index"]
                if self.config["completehtmlfileextension"]==True and os.path.isfile(uri+".html"):
                    uri+=".html"
        try:
            if "pyhp" in self.server.extensions and self.config["primeforpyhp"]==True: ## PyHp
                pyhpconfig=self.server.extensions["pyhp"].config
                if os.path.exists(uri+".pyhp"):
                    uri+=".pyhp"
                if uri[-1]=="/" and os.path.exists(uri+pyhpconfig["index"]):
                    uri+=pyhpconfig["index"]
        except:
            traceback.print_exc()
        incoming.rqstdt["uri"]=uri
