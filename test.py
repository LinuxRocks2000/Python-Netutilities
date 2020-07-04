import serverutils

s=serverutils.SimpleWebServer("",8080,sitedir="test")
##s.addExtension(serverutils.SimpleGzipper())
s.start()
