class Controls:
    def __init__(self,server):
        ''' Another "Extend-The-Class". This time only override on_post and on_get (same args as the corresponding functions in the server),
            and inittasks, which is only passed a self argument and is run once (like in the server).

            Pass in your finished class itself as the controls argument in your server.
            '''
        self.server=server
        self.inittasks()
    def inittasks(self):
        pass
    def on_post(self,data,connection):
        connection.send("You seem to have stumbled across an unfinished controls")
        connection.close()
    def on_get(self,data,connection):
        connection.send("You seem to have stumbled across an unfinished controls")
        connection.close()
