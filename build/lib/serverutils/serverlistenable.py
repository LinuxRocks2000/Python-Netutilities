from .socketutils import ServerSocket


pork=print
printtabs=""
def addprinttabs(n):
    global printtabs
    printtabs+=n*"  "
def removeprinttabs(n):
    global printtabs
    printtabs=printtabs[n*2:]
def print(*args,**kwargs):
    global printtabs
    dawrgs=list(args)
    dawrgs[0]=printtabs+dawrgs[0]
    pork(*dawrgs,**kwargs)
class Hook:
    def __init__(self,name,controller=None):
        self.name=name
        self.controller=controller or self._call
        self.functions=[]
        self.default=None
        self.eventual=None
        self.topfunctions=[] ## Top functions override all the others. These are sorted by priority, and must return "True" or "False" (determining whether or not to continue)
    def _call(self,*args,**kwargs):
        print("Beginning hook name = "+self.name)
        addprinttabs(1)
        if self.doesAnything(): ## Allow for a "default function" which will only run if nothing else is available. So far, no one has used new controller functions!
            continu=True
            for x in self.topfunctions:
                if continu:
                    print("Doing a top function, hook name = "+self.name+", function name = "+x.__name__)
                    continu=x(*args,**kwargs)
                    print("Did the top function, hook name = "+self.name+", continu = "+str(continu))
            print("Finished doing the top functions for "+self.name)
            if continu:
                for x in self.functions:
                    print("Doing a function, hook name = "+self.name+", function name = "+x.__name__)
                    x(*args,**kwargs)
                    print("Did the function, hook name = "+self.name)
                print('Finished doing the normal functions for '+self.name)
        elif self.default:
            print("Doing the default function, hook name = "+self.name)
            self.default(*args,**kwargs)
            print("Did the default function, hook name = "+self.name)
        print("Eventual in "+self.name+":",self.eventual)
        if self.eventual:
            print("Doing the eventual function, hook name = "+self.name)
            self.eventual(*args,**kwargs)
            print("Did the eventual function, hook name = "+self.name)
        removeprinttabs(1)
        print("Ended hook name = "+self.name)
    def call(self,*args,**kwargs):
        self.controller(*args,**kwargs)
    def addFunction(self,function):
        self.functions.append(function)
    def addTopFunction(self,function,p=None):
        priority=p or len(self.topfunctions)+1000
        self.topfunctions.insert(priority,function)
        ## Lower numbers = higher priority. No priority value = minimum priority.
        ## It is likely that this will mainly be used for security protocols, such as blocking 
        ## the continuation of an HTTP request if the username and password are invalid.
    def delTopFunction(self,function):
        self.topfunctions.remove(function)
    def delFunction(self,function):
        self.functions.remove(function)
    def setDefaultFunction(self,function):
        self.default=function
    def setEventualFunction(self,function):
        self.eventual=function
        print("Set the eventual function")
    def doesAnything(self):
        if len(self.topfunctions)+len(self.functions)>0:
            return True
        return False


class TCPServer:
    def __init__(self,host,port,blocking=True,*args,**kwargs):
        self.server=ServerSocket(host,port,blocking=blocking)
        self.blocking=blocking
        self.host=host
        self.port=port
        self.extensions={}
        self.functable={}
        self.protocols={}
        self.hooks={}
        init=self.addHook('init')
        init.addFunction(self.listen)
        main=self.addHook("mainloop")
        main.addFunction(self.run)
        main.addFunction(self.tasks)
        handle=self.addHook("handle")
        handle.addFunction(self.handle)
        self.inittasks(*args,**kwargs)
    def inittasks(self,*args,**kwargs):
        pass
    def listen(self,lst=5):
        self.server.listen(lst)
    def tasks(self):
        pass
    def addExtension(self,extensionobject):
        self.protocols[extensionobject.addToServer(self)]=extensionobject
    def addProtocol(self,protocolObject):
        self.protocols[protocolObject.addToServer(self)]=protocolObject
    def run(self):
        connection=self.server.get_connection()
        data=connection.recvall()
        if connection: self.getHook("handle").call(connection,data)
    def getHook(self,hook):
        return self.hooks[hook]
    def addHook(self,hook):
        h=Hook(hook)
        self.hooks[hook]=h
        return h
    def delHook(self,hook):
        del self.hooks[hook]
    def handle(self,connection,data):
        pass
    def start(self,*args,**kwargs):
        self.getHook("init").call(*args,**kwargs)
        while 1:
            self.getHook("mainloop").call() ## Mainloop functions must not have args
    def addFuncToTable(self,name,function):
        self.functable[name]=function
    def callFuncFromTable(self,name,*args,**kwargs):
        self.functable[name](*args,**kwargs)
    def delFuncFromTable(self,name):
        del self.functable[name]
