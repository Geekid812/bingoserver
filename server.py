import aiohttp
import asyncio

from rest import USER_AGENT

# Holds global state in the server
class GameServer:
    # GameServer is a singleton
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance:
            return cls._instance
        
        cls._instance = GameServer()
        return cls._instance

    def __init__(self):
        self.http = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
        self.rooms = []
        self.clients = []

    async def disconnect(self, client):
        client.writer.close()
        self.clients.remove(client)
        for room in self.rooms:
            if client in [player.socket for player in (room.members + [room.host])]:
                await room.on_client_disconnect(client)

    def find_client(self, login):
        for client in self.clients:
            if client.matches(login): return client

    def find_player(self, login):
        for room in self.rooms:
            for player in (room.members + [room.host]):
                if player.matches(login):
                    return room, player
        
        return None, None
    
    def find_room(self, code):
        for room in self.rooms:
            if room.code == code: return room
        
        return None
