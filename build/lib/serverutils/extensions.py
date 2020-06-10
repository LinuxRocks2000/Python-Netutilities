import json
import os
from .protocols import HFE


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
