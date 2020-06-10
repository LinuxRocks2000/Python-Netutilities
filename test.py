from serverutils import SimpleHTTPServer ## Get the not-yet-bled edge before release
from serverutils import VeryBasicSecurity
class MyServer(SimpleHTTPServer):
    def handlepost(self,incoming,outgoing):
        print("A post request slipped through the bounds.")

s=MyServer("",8080,sitedir="test")
s.addExtension(VeryBasicSecurity(configfile="test/config.json",default=2)) ## Low security server. Anyone can access anything (until I add a usermanager).
s.start()
