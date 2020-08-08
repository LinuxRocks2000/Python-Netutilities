import serverutils
import traceback


class TemplateablePage:
    def __init__(self,page):
        self.page=page
    def getPage(self,template):
        return self.page.format(**template)


class MyServer(serverutils.TCPServer):
    def inittasks(self,*args,**kwargs):
        self.authed=[]
        self.normalpage=TemplateablePage('<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>The page you are visiting is: {name}</h1><h2>{authstate}</h2></body></html>')
    def httprecieve(self,incoming):
        try:
            print(incoming.rqstdt["uri"])
        except:
            traceback.print_exc()


s=None
try:
    s=MyServer("",8080,blocking=False)
    print("8080")
except OSError:
    try:
        s=MyServer("",8070,blocking=False)
        print("8070")
    except OSError:
        s=MyServer("",8060,blocking=False)
        print("8060")


s.addProtocol(serverutils.Protocol_HTTP())
s.addExtension(serverutils.URISterilizer())
websconfig={"404":["inline","404 you are an idiot to think that this was found."],
            "sitedir":"test"}
s.addExtension(serverutils.IncrediblySimpleWebSend(config=websconfig))

s.start()
