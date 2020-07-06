import serverutils

s=serverutils.SimpleWebServer("",8060,sitedir="test")
s.addExtension(serverutils.SimpleGzipper())
s.start()
