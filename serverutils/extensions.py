import json
import os
import sys
from .protocols import HFE, HTTPDATA
import importlib
import gzip


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


class VeryBasicSecurity(Extension):
    '''Incredibly simple security measures for servers. Blocks GET and POST requests
which attempt to access secured files. Pass in the filename of a JSON
config file, and the default permission level. See source for more.'''
    def inittasks(self,configfile='config.json',default=1): ## Default permissions is... Dun dun dun... READ!
        self.fname=configfile
        file=open(configfile)
        self.data=json.load(file)
        file.close()
        print(self.data)
        self.defaultPermissions=default
    def uponAddToServer(self):
        self.server.getHook("http_handleGET").addTopFunction(self.topGET,0)
        self.server.getHook("http_handlePOST").addTopFunction(self.topPOST,0)
    def topPOST(self,incoming,outgoing):
        perms=self.getPermissions(incoming.location,incoming)
        print("Intercepting a post request...")
        if perms>=2:
            print("Post request supplied")
            return True ## Write access granted beep boop baap
        elif perms<2 and perms>-1:
            self.server.getHook("httpfailure").call(incoming,outgoing,HFE.PERMISSIONDENIED)
            return False
        else:
            self.server.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND)
            return False
    def topGET(self,incoming,outgoing):
        print("Intercepting a get request...")
        perms=self.getPermissions(incoming.location,incoming)
        if perms>=1:
            return True ## Anyone can access this. User managers should step in for additional security.
        elif perms==0:
            self.server.getHook("httpfailure").call(incoming,outgoing,HFE.PERMISSIONDENIED)
            return False
        else:
            self.server.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND)
            return False
    def getPermissions(self,url,incoming):
        perms=self.defaultPermissions ## Follows the UNIX fashion, except more limited. One number, regulates public access ONLY. User managers should step in afterwards for user-only stuff.
        ## Permission numbers can be either -1, 0, 1, 2, or 3. -1 means classified, so a 404, 0 means no perms, 1 means read, 2 means write, 3 means both. Post requests are write, obviously.
        print(os.path.basename(url))
        if os.path.basename(url) in self.data["public"]:
            print("Using public perms")
            perms=self.data["public"][url]
        return perms


class JustASimpleWebServerExtension(Extension):
    '''An extension for a simple web server.'''
    def inittasks(self,sitedir=".",index="index.html"):
        self.sitedir=sitedir if sitedir[-1]=="/" else sitedir+"/" ## Sterilizer uses this, not me.
        self.index=index
    def uponAddToServer(self):
        self.server.getHook("http_handleGET").addTopFunction(self.topGET,0) ## Not to make it a habit, but priority number 0 is kind of necessary for webserver extensions.
        self.server.getHook("http_handle").addTopFunction(self.filter_reqloc,0)
        self.server.getHook("httpfailure").setDefaultFunction(self.fail)
        return "jaswse"
    def fail(self,incoming,outgoing,event):
        if event==HFE.FILENOTFOUND:
            outgoing.setStatus(404)
            outgoing.setContent("The file you does be lookin' for don't exist.")
    def topGET(self,incoming,outgoing): ## Copycatted from server.py/SimpleHTTPServer
        baselocale=os.path.basename(incoming.location)
        locale=incoming.location
        if baselocale=="":
            if os.path.isfile(locale+self.index):
                outgoing.setStatus(200)
                outgoing.setFile(locale+self.index)
            else:
                self.server.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND) ## Build utilities should intercept this.
        else:
            if os.path.isfile(locale):
                outgoing.setStatus(200)
                outgoing.setFile(locale)
            elif os.path.isdir(locale) and os.path.exists(locale+"/"+self.index):
                outgoing.setStatus(200)
                outgoing.setFile(locale+"/"+self.index)
            elif os.path.isfile(locale+".html"):
                outgoing.setStatus(200)
                outgoing.setFile(locale+".html")
            else:
                self.server.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND)
                return False ## Don't continue if the HTTP failed
        print("Made it out of the TopGet function in JaSWSE")
        return True
    def filter_reqloc(self,incoming,outgoing):
        '''Sterilize the location of the request. Do not touch unless you know what your doing.'''
        realpos=incoming.location
        realpos=realpos.replace("/../","/") ## Make sure unsavory characters can't hack you out by sending get requests with ../ as the location
        if realpos[0]=="/":
            realpos=realpos[1:]
        realpos=self.sitedir+realpos
        incoming.location=realpos
        print("Successfully filtered the request location in JaSWSE")
        return True ## Don't ever forget return in a top function.


class PyHP(Extension):
    def uponAddToServer(self,index="index"):
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
            if incoming.location[-1]=="/" and os.path.exists(incoming.location+self.index+".py"):
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


class HTTPProtocolSwitcher(Extension):
    def uponAddToServer(self,server):
        server.getHook("http_handle").addTopFunction(self.handle)
        self.switchhook=server.addHook("protocolswitcher_switch")
    def handle(self,incoming,outgoing):
        if incoming.type=="GET" and incoming.headers["Connection"]=="upgrade":
            self.switchhook.call(incoming.headers["Upgrade"],incoming,outgoing)
            outgoing.setStatus(101)
            outgoing.addHeader("Upgrade",incoming.headers["Upgrade"])
            outgoing.addHeader("Connection","upgrade")
            return False
        return True


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
            data+=x+" : "+y+"\n"
        file.write(data)
        file.close()
    def openCache(self):
        file=open(self.cachelocale+"md5caches")
        data=file.read()
        file.close()
        d=data.split("\n")[:-1] ## Use all but the last, unfilled, line.
        returner={}
        for x in d:
            ps=x.split(" = ")
            returner[ps[0]]=float(ps[1])
        return returner
    def handle(self,incoming,outgoing):
        ## Only do any of this if outgoing has a file send
        print("Beep")
        if outgoing.filename and os.path.exists(incoming.location) and "gzip" in incoming.headers["Accept-Encoding"]:
            print(incoming.location)
            if self.isCacheInvalid(incoming.location):
                self.validateCache(incoming.location)
                file=open(incoming.location)
                data=file.read() ## SimpleGzipper is NOT MEMORY SAFE. But none of this is.
                file.close()
                gzipped=gzip.GzipFile('"'+self.cachelocale+incoming.location+'.gz"',"wb+")
                output.write(data)
                output.close()
            outgoing.setFile('"'+self.cachelocale+incoming.location+'.gz"')
            outgoing.addHeader("Content-Encoding","gzip")
        else:
            server.getHook("httpfailure").call(incoming,outgoing,HFE.FILENOTFOUND)
        print("Made it past the get request intercepter for SimpleGzipper")
        return True
