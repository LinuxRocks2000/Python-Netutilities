# A wrapper written for the Python websockets api. Created by Tyler Clarke, March 10, 2020. This software is free to
# modify and distribute under the terms of any freeware license you care to mention. Just keep these three lines.

# Either create a SimpleServer object and add listener functions, or for more functionality (and cleaner code)
# extend the WebsocketListenable class.

import asyncio
import json
import websockets


class Events:
    PONG = "AA"
    PING = "AB"
    SENDUPD = "AC"
    RECVUPD = "AD"
    AUXILIARY_POST = "AE"
    AUXILIARY_GET = "AF"
    BREAK = "horseyaklsdfja;sldfja;sldkfja;sdljfka;sdlkfja;sdlfkja;dslkjfalsdfjk;alsdkjf;alskdjf;alsdkfj;asdlkjf;aslkdfj;aslkdjf"
    USERON = "BA"

class WebSocketListenable:
    def __init__(self, port):
        self.server = websockets.serve(self._useron, port=port)
        self.clients = {}

    async def run(self):
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().create_task(self.loop)
        asyncio.get_event_loop().run_forever()

    async def _useron(self, websocket, path):
        uit = self._getemptyuid()
        self.clients[uit] == [websocket, path]
        websocket.send(uit)

    async def main(self, websocket, path):
        async for x in websocket:
            evt = json.loads(x)
            if evt["event"] == Events.PING:
                websocket.send(Events.PONG)
            elif evt['event'] == Events.PONG:
                websocket.send(Events.BREAK)
            elif evt["event"] == Events.AUXILIARY_GET:
                await self.handle_auxget(evt, path)
            elif evt["event"] == Events.AUXILIARY_POST:
                await self.handle_auxpost(evt, path)
            elif evt["event"] == Events.SENDUPD:
                await self.handle_updatefromclient(evt, path)
            elif evt["event"] == Events.RECVUPD:
                await self.handle_clientrequestupdate(evt, path)
            elif evt["event"] == Events.USERON:
                await self._useron(websocket,path)

    async def loop(self):
        pass

    async def handle_updatefromclient(self, event, path):
        pass

    async def handle_clientrequestupdate(self, event, path):
        pass

    async def handle_auxget(self, event, path):
        pass

    async def handle_auxpost(self, event, path):
        pass

    def _getemptyuid(self):
        d = 0
        for x in self.clients:
            if d == x:
                d += 1
        return d
