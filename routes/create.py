import asyncio
from aiohttp import web
from json import dumps

from config import REQUIRED_VERSION
from client import ClientTCPSocket
from server import GameServer
from room import GameRoom, GamePlayer
from util.version import is_version_greater

async def create(request: web.Request):
    body = await request.json()
    server = GameServer.instance()
    client = server.find_client(body['client_secret'])

    if not is_version_greater(REQUIRED_VERSION, body['version']):
        return web.Response(status=426)

    if not client:
        # Client is not connected via the TCP port
        return web.Response(status=400)

    host = GamePlayer(client, body['name'], None)

    room = GameRoom(host, body['size'], body['selection'], body['medal'])
    asyncio.create_task(room.initialize_maplist())
    server.rooms.append(room)
    
    return web.Response(text=dumps({
        'room_code': room.code,
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
            for team in room.teams
        ]
    }))
