import asyncio
from string import ascii_uppercase, digits
import random
from json import dumps
from datetime import datetime

from client import ClientTCPSocket
from models import MapSelection, Medal, Team, BingoDirection, LoadStatus
from rest.tmexchange import get_random_maps

ROOMCODE_LENGTH = 6

class GamePlayer:
    def __init__(self, socket: ClientTCPSocket, username: str, team: int = 0):
        self.socket = socket
        self.name = username
        self.team = team

    def matches(self, secret: str):
        return self.socket.matches(secret)
    
class GameRoom:
    def __init__(self, host: GamePlayer, size: int, selection: MapSelection, medal: Medal):
        self.server = host.socket.server
        self.code = roomcode_generate()
        self.host = host
        self.size = size
        self.selection = selection
        self.medal = medal
        self.members: list[GamePlayer] = []
        self.maplist = []
        self.mapload_failed = False
        self.created = datetime.utcnow()
        self.started = datetime.fromtimestamp(-1)

    def has_started(self):
        return int(self.started.timestamp()) != -1
    
    def is_start_intro(self):
        return self.has_started() and self.started > datetime.utcnow()

    def loading_status(self):
        if self.mapload_failed: return LoadStatus.LOAD_FAIL
        if len(self.maplist) >= 25: return LoadStatus.LOAD_SUCCESS
        return LoadStatus.LOADING

    async def initialize_maplist(self):
        self.maplist = await get_random_maps(self.server.http, self.selection, 25)
        if len(self.maplist) < 25:
            self.mapload_failed = True

        if not self.host:
            return # Room and Player got deleted
        await self.broadcast(dumps({
            "method": "MAPS_LOAD_STATUS",
            "status": self.loading_status()
        }))
    
    async def on_client_remove(self, socket):
        for member in self.members:
            if member.socket == socket:
                self.members.remove(member)
                await self.broadcast_update()
        
        if self.host.socket == socket:
            self.host = None
            # TODO: disconnect all
            socket.server.rooms.remove(self)
    
    async def broadcast(self, message: str):
        await asyncio.gather(*[
            player.socket.write(message) for player in (self.members + [self.host])
        ])

    async def broadcast_update(self):
        data = dumps({
            'method': 'ROOM_UPDATE',
            'members': [
                {
                    'name': player.name,
                    'team': player.team,
                }
                for player in (self.members + [self.host])
            ]
        })

        await self.broadcast(data)
    
    async def broadcast_start(self):
        data = dumps({
            'method': 'GAME_START',
            'time': self.started.timestamp(),
            'maplist': [
                {
                    'name': gamemap.name,
                    'author': gamemap.author,
                    'tmxid': gamemap.tmxid,
                    'uid': gamemap.uid
                }
                for gamemap in self.maplist
            ]
        })

        await self.broadcast(data)

    async def broadcast_claim(self, player, mapname, cellid, time, medal, improve, delta):
        data = dumps({
            'method': 'CLAIM_CELL',
            'playername': player.name,
            'mapname': mapname,
            'team': player.team,
            'cellid': cellid,
            'time': time,
            'medal': medal,
            'improve': improve,
            'delta': delta
        })

        await self.broadcast(data)
    
    async def broadcast_end(self, winner_team, direction, offset):
        data = dumps({
            'method': 'GAME_END',
            'winner': winner_team,
            'bingodir': direction,
            'offset': offset
        })

        await self.broadcast(data)

    async def check_winner(self):
        # Rows
        for row in range(5):
            for team in [Team.RED, Team.BLUE]:
                if all([self.maplist[5 * row + i].team == team for i in range(5)]):
                    return await self.broadcast_end(team, BingoDirection.HORIZONTAL, row)

        # Columns
        for column in range(5):
            for team in [Team.RED, Team.BLUE]:
                if all([self.maplist[5 * i + column].team == team for i in range(5)]):
                    return await self.broadcast_end(team, BingoDirection.VERTICAL, column)

        # 1st diagonal 
        for team in [Team.RED, Team.BLUE]:
            if all([self.maplist[6 * i].team == team for i in range(5)]):
                return await self.broadcast_end(team, BingoDirection.DIAGONAL, 0)
        
        # 2nd diagonal
        for team in [Team.RED, Team.BLUE]:
            if all([self.maplist[4 * (i + 1)].team == team for i in range(5)]):
                return await self.broadcast_end(team, BingoDirection.DIAGONAL, 1)

def roomcode_generate():
    """Generates a random code consisting of uppercase letters and digits"""
    return "".join(random.choices(ascii_uppercase + digits, k=ROOMCODE_LENGTH))
