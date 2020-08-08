import json
import os
import sys
from .protocols import HFE, HTTPDATA, HTTPOutgoing
import importlib
import gzip, shutil


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
    def uponAddToServer(self,index="index.py"):
        print("Added to server")
        self.index=index
        self.server.getHook("http_handle").addFunction(self.handle)
        return "pyhp" ## Extensions should always return a name
    def handle(self,incoming,outgoing):
        try:
            locale=None
            if incoming.location[-3:]==".py":
                locale=incoming.location[:-3]
            if os.path.exists(incoming.location+".py"):
                locale=incoming.location
            print(incoming.location)
            if incoming.location[-1]=="/" and os.path.exists(incoming.location+self.index):
                locale=incoming.location+self.index
            if locale:
                i=importlib.import_module(os.path.relpath(locale).replace("/","."))
                for x in HTTPDATA.methods:
                    if hasattr(i,"handle_"+x.lower()):
                        data,status=i.__getattribute__("handle_"+x.lower())(incoming)
                        outgoing.setStatus(status)
                        outgoing.setContent(data)
        except Exception as e:
            print(e)


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
        self.server.getHook("http_handleGET").addFunction(self.handle)
        print("SimpleGzipper has been added!")
        return "SimpleGzipper"
    def isCacheInvalid(self,filename):
        print("Checking SimpleGzipper cache...")
        data=self.openCache()
        crmtime=os.path.getmtime(filename)
        if (not filename in data) or (crmtime!=data[filename]):
            return True
        return False
    def validateCache(self,filename):
        print("Validating SimpleGzipper cache...")
        d=self.openCache()
        d[filename]=str(os.path.getmtime(filename))
        self.writeCache(d)
    def writeCache(self,ncache):
        print("Writing SimpleGzipper cache")
        file=open(self.cachelocale+"md5caches","w")
        data=""
        for x,y in ncache.items():
            data+=str(x)+" : "+str(y)+"\n"
        file.write(data)
        file.close()
    def openCache(self):
        print("Opening SimpleGzipper cache")
        file=open(self.cachelocale+"md5caches")
        data=file.read()
        file.close()
        print(data)
        d=data.split("\n")[:-1] ## Use all but the last, unfilled, line.
        print(d)
        returner={}
        for x in d:
            ps=x.split(" : ")
            print(ps)
            returner[ps[0]]=float(ps[1])
        return returner
    def handle(self,incoming,outgoing):
        ## Only do any of this if outgoing has a file send
        print("Handling, in SimpleGzipper")
        if os.path.isfile(incoming.location) and outgoing.filename and "gzip" in incoming.headers["Accept-Encoding"]:
            print("Made it past the first IfGate in SimpleGzipper/handle")
            location=incoming.location.replace("/",".")
            if self.isCacheInvalid(incoming.location):
                print("SimpleGzipper cache is invalid for "+location)
                self.validateCache(incoming.location)
                file=open(incoming.location,"rb")
                gzipped=gzip.open(self.cachelocale+'"'+location+'.gz"',"wb")
                shutil.copyfileobj(file,gzipped)
                file.close()
                gzipped.close()
            outgoing.setFile(self.cachelocale+'"'+location+'.gz"')
            outgoing.addHeader("Content-Encoding","gzip")
        return True


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
            o=HTTPOutgoing(incoming)
            if os.path.isfile(incoming.rqstdt["uri"]):
                o.setFile(incoming.rqstdt["uri"])
            else:
                if self.config["404"][0]=="inline":
                    o.setContent(self.config["404"][1])
                elif self.config["404"][0]=="file":
                    o.setFile(self.config["404"][1])
            o.send()


class URISterilizer(Extension):
    def inittasks(self,config={}):
        self.config={"relativepaths":True,"noparentdir":True,"primeforwebsend":True,"useindexindirectory":True,"completehtmlfileextension":True}
        self.config.update(config)
    def uponAddToServer(self):
        self.server.getHook("httprecv").addFunction(self.httprecv)
        return "URISterilizer"
    def httprecv(self,incoming):
        uri=incoming.rqstdt["uri"]
        print(uri)
        if self.config["relativepaths"]==True and uri[0]=="/": uri=uri[1:]
        if self.config["noparentdir"]==True and "../" in uri: uri.replace("../","")
        if self.config["primeforwebsend"]==True: ## Designed for compatibility with the WebSend family of HTTP server senders
            print(self.server.extensions)
            if "IS-Websend" in self.server.extensions: ## Incredibly Simple WebSend
                websconfig=self.server.extensions["IS-Websend"].config
                uri=websconfig["sitedir"]+("/" if not websconfig["sitedir"][-1]=="/" else "")+uri
                print(uri+("/" if uri[-1]!="/" else "")+websconfig["index"])
                if self.config["useindexindirectory"]==True and os.path.isfile(uri+("/" if not uri[-1]=="/" else "")+websconfig["index"]):
                    uri+=("/" if not uri[-1]=="/" else "")+websconfig["index"]
                if self.config["completehtmlfileextension"]==True and os.path.isfile(uri+".html"):
                    uri+=".html"
        incoming.rqstdt["uri"]=uri
