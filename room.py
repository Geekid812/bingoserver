import asyncio
from string import ascii_uppercase, digits
import random
from json import dumps
from datetime import datetime

from config import ROOMCODE_CHARACTERS
from client import ClientTCPSocket
from models import MapSelection, Medal, BingoDirection, LoadStatus
from gameteam import GameTeam
from rest.tmexchange import get_random_maps

ROOMCODE_LENGTH = 6

class GamePlayer:
    def __init__(self, socket: ClientTCPSocket, username: str, team: GameTeam = None):
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
        self.teams: list[GameTeam] = [
            GameTeam(index + 1, color[0], color[1])
            for index, color in enumerate(random.sample(list(GameTeam.colors.items()), 2))
        ]
        self.host.team = self.teams[0]
        
        self.members: list[GamePlayer] = []
        self.maplist = []
        self.mapload_failed = False
        self.created = datetime.utcnow()
        self.started: datetime = None

    def find_team(self, id: int) -> GameTeam:
        for team in self.teams:
            if team.id == id:
                return team

    def has_started(self):
        return self.started is not None
    
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
    
    async def on_client_remove(self, socket: ClientTCPSocket):
        if self.host and self.host.socket == socket:
            self.host = None
            if not self.has_started(): # Only close room if not started yet
                socket.server.rooms.remove(self)
                for member in self.members:
                    member.socket.closed = True
                await self.broadcast_close() # final message
        else:
            for member in self.members:
                if member.socket == socket:
                    self.members.remove(member)
                    await self.broadcast_update()

    
    async def broadcast(self, message: str):
        await asyncio.gather(*[
            player.socket.write(message) for player in (self.members + [self.host]) if player
        ])

    async def broadcast_update(self):
        data = dumps({
            'method': 'ROOM_UPDATE',
            'teams': [
                {
                    'id': team.id,
                    'name': team.name,
                    'color': {
                        'r': team.color[0],
                        'g': team.color[1],
                        'b': team.color[2]
                    }
                }
                for team in self.teams
            ],
            'members': [
                {
                    'name': player.name,
                    'team_id': player.team.id,
                }
                for player in (self.members + [self.host]) if player
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

    async def broadcast_close(self):
        data = dumps({
            'method': 'ROOM_CLOSED'    
        })
        
        await self.broadcast(data)

    async def broadcast_claim(self, player, mapname, cellid, time, medal, improve, delta):
        data = dumps({
            'method': 'CLAIM_CELL',
            'playername': player.name,
            'mapname': mapname,
            'team_id': player.team.id,
            'cellid': cellid,
            'time': time,
            'medal': medal,
            'improve': improve,
            'delta': delta
        })

        await self.broadcast(data)
    
    async def broadcast_end(self, team: GameTeam, direction, offset):
        data = dumps({
            'method': 'GAME_END',
            'team_id': team.id,
            'bingodir': direction,
            'offset': offset
        })

        await self.broadcast(data)

    async def check_winner(self):
        # Rows
        for row in range(5):
            for team in self.teams:
                if all([self.maplist[5 * row + i].team == team for i in range(5)]):
                    return await self.broadcast_end(team, BingoDirection.HORIZONTAL, row)

        # Columns
        for column in range(5):
            for team in self.teams:
                if all([self.maplist[5 * i + column].team == team for i in range(5)]):
                    return await self.broadcast_end(team, BingoDirection.VERTICAL, column)

        # 1st diagonal 
        for team in self.teams:
            if all([self.maplist[6 * i].team == team for i in range(5)]):
                return await self.broadcast_end(team, BingoDirection.DIAGONAL, 0)
        
        # 2nd diagonal
        for team in self.teams:
            if all([self.maplist[4 * (i + 1)].team == team for i in range(5)]):
                return await self.broadcast_end(team, BingoDirection.DIAGONAL, 1)

def roomcode_generate():
    """Generates a random code consisting of uppercase letters and digits"""
    return "".join(random.choices(ROOMCODE_CHARACTERS, k=ROOMCODE_LENGTH))
