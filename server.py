import aiohttp
import asyncio

from config import USER_AGENT
from room import GamePlayer, GameRoom
from client import ClientTCPSocket

# Holds global state in the server
class GameServer:
    # GameServer is a singleton
    _instance: "GameServer" = None

    @classmethod
    def instance(cls):
        if cls._instance:
            return cls._instance
        
        cls._instance = GameServer()
        return cls._instance

    def __init__(self):
        self.http = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
        self.rooms: list[GameRoom] = []
        self.clients: list[ClientTCPSocket] = []

    async def remove_client(self, client: ClientTCPSocket):
        if client in self.clients:
            self.clients.remove(client)
        for room in self.rooms:
            if client in [player.socket for player in (room.members + [room.host]) if player]:
                await room.on_client_remove(client)
                if len([player for player in room.members + [room.host] if player]) == 0:
                    self.rooms.remove(room)

    def find_client(self, secret: str) -> ClientTCPSocket:
        for client in self.clients:
            if client.secret == secret: return client

    def find_player(self, secret: str) -> tuple[GameRoom, GamePlayer]:
        for room in self.rooms:
            for player in (room.members + [room.host]):
                if player and player.matches(secret):
                    return room, player
        
        return None, None
    
    def find_room(self, code: str) -> GameRoom:
        for room in self.rooms:
            if room.code == code: return room
        
        return None
