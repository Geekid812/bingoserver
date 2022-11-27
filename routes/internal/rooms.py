from aiohttp import web
from json import dumps

from server import GameServer

async def rooms_status(request: web.Request):
    server = GameServer.instance()
    return web.Response(text=dumps([
        {
            'host': room.host and room.host.name,
            'size': room.size,
            'selection': room.selection.mode,
            'medal': room.medal,
            'started': str(room.started),
            'created': str(room.created),
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
            ],
            'members': [
                member.name
                for member in room.members
            ]
        }
        for room in server.rooms
    ]), content_type='application/json')
