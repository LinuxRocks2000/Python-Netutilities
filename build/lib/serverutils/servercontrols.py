class Controls:
    def __init__(self,server):
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
