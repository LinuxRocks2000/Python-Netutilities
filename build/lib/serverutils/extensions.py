import json
import os
import sys
from .protocols import HFE
import importlib

## Classes for Extensions. Such as, the JSONIndexedSecurity.
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
    def inittasks(self,sitedir=".",index="index.html"):
        self.sitedir=sitedir if sitedir[-1]=="/" else sitedir+"/" ## Sterilizer uses this, not me.
        self.index=index
    def uponAddToServer(self):
        self.server.getHook("http_handleGET").addTopFunction(self.topGET,0) ## Not to make it a habit, but priority number 0 is kind of necessary for webserver extensions.
        self.server.getHook("http_handle").addTopFunction(self.filter_reqloc)
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
        
    def filter_reqloc(self,incoming,outgoing):
        '''Sterilize the location of the request. Do not touch unless you know what your doing.'''
        realpos=incoming.location
        if realpos[0]=="/":
            realpos=realpos[1:]
        realpos=self.sitedir+realpos
        realpos=realpos.replace("/../","/") ## Make sure unsavory characters can't hack you out by sending get requests with ../ as the location
        incoming.location=realpos
        print("Filtered the request location")
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
                if incoming.type=="GET" and hasattr(i,"handle_get"):
                    data,status=i.handle_get(incoming) ## The PyHP file should return HTML and HTTP status
                    outgoing.setStatus(status)
                    outgoing.setContent(data)
                elif incoming.type=="POST" and hasattr(i,"handle_post"):
                    status=i.handle_post(incoming) ## For POST, PyHP should return the HTTP status code
                    outgoing.setStatus(status)
        except Exception as e:
            print(e)
