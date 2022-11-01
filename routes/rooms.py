from aiohttp import web
from json import dumps

from server import GameServer

async def rooms_status(request: web.Request):
    server = GameServer.instance()
    return web.Response(text=dumps([
        {
            'host': room.host.name,
            'size': room.size,
            'selection': room.selection,
            'medal': room.medal,
            'started': room.started,
            'created': str(room.created),
            'members': [
                member.name
                for member in room.members
            ]
        }
        for room in server.rooms
    ]), content_type='application/json')
