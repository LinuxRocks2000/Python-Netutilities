from .socketutils import ServerSocket


class Hook:
    def __init__(self,name,controller=None):
        self.name=name
        self.controller=controller or self._call
        self.functions=[]
        self.default=None
        self.eventuals=[]
        self.topfunctions=[] ## Top functions override all the others. These are sorted by priority, and must return "True" or "False" (determining whether or not to continue)
    def _call(self,*args,**kwargs):
        if self.doesAnything(): ## Allow for a "default function" which will only run if nothing else is available. So far, no one has used new controller functions!
            continu=True
            for x in self.topfunctions:
                try:
                    if continu:
                        continu=x(*args,**kwargs)
                except:
                    pass#print("A top function named "+x.__name__+" failed")
            if continu:
                for x in self.functions:
                    try:
                        x(*args,**kwargs)
                    except Exception as e:
                        pass#print("A normal function named "+x.__name__+" failed with exception "+str(e))
        elif self.default:
            try:
                self.default(*args,**kwargs)
            except:
                pass#print("A default function failed.")
        for x in self.eventuals:
            try:
                x(*args,**kwargs)
                pass#print("An eventual function named "+x.__name__+" succeeded, and Yay!")
            except:
                pass#print("An eventual function named "+x.__name__+" failed, however it was caught.")
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
    def addEventualFunction(self,function,priority=None):
        if priority==None:
            self.eventuals.append(function)
        else:
            self.eventuals.insert(function,priority)
    def doesAnything(self):
        if len(self.topfunctions)+len(self.functions)+len(self.eventuals)>0:
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
        self.protocol=None
        self.hooks={}
        init=self.addHook('init')
        main=self.addHook("mainloop")
        main.addFunction(self._run)
        self.inittasks(*args,**kwargs)
        self.clients=[]
    def inittasks(self,*args,**kwargs):
        pass
    def connect(self,client):
        pass
    def run(self):
        pass
    def addExtension(self,extensionobject):
        self.extensions[extensionobject.addToServer(self)]=extensionobject
    def addProtocol(self,protocolObject):
        self.protocol=protocolObject
        protocolObject.addToServer(self)
    def _run(self):
        connection=self.server.get_connection()
        if connection:
            if self.protocol:
                self.protocol.connect(connection)
            else:
                self.connect(connection)
                self.clients.append(connection)
        if not self.protocol:
            self.run()
        else:
            self.protocol.run()
    def getHook(self,hook):
        return self.hooks[hook]
    def addHook(self,hook):
        h=Hook(hook)
        self.hooks[hook]=h
        return h
    def delHook(self,hook):
        del self.hooks[hook]
    def start(self,*args,**kwargs):
        self.getHook("init").call(*args,**kwargs)
    def iterate(self):
        self.getHook("mainloop").call() ## Mainloop functions must not have args
    def addFuncToTable(self,name,function):
        self.functable[name]=function
    def callFuncFromTable(self,name,*args,**kwargs):
        self.functable[name](*args,**kwargs)
    def delFuncFromTable(self,name):
        del self.functable[name]
