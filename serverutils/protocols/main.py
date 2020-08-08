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
