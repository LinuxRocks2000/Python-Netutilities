from .socketutils import ServerSocket

class Hook:
    def __init__(self,name,controller=None):
        self.name=name
        self.controller=controller or self._call
        self.functions=[]
        self.default=None
        self.topfunctions=[] ## Top functions override all the others. These are sorted by priority, and must return "True" or "False" (determining whether or not to continue)
    def _call(self,*args,**kwargs):
        if len(self.functions)+len(self.topfunctions)>0: ## Allow for a "default function" which will only run if nothing else is available. So far, no one has used new controller functions!
            continu=True
            for x in self.topfunctions:
                if continu:
                    continu=x(*args,**kwargs)
            if continu:
                for x in self.functions:
                    x(*args,**kwargs)
        elif self.default:
            self.default(*args,**kwargs)
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
