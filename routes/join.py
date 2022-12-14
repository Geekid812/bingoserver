from aiohttp import web
from json import dumps

from config import REQUIRED_VERSION
from server import GameServer
from room import GamePlayer
from util.version import is_version_greater

async def join_room(request: web.Request):
    body = await request.json()
    server = GameServer.instance()
    client = server.find_client(body['client_secret'])

    if not is_version_greater(REQUIRED_VERSION, body['version']):
        return web.Response(status=426)

    if not client:
        # Client is not connected via the TCP port
        return web.Response(status=400)

    room = server.find_room(body['code'])
    if not room:
        return web.Response(status=204) # Room not found
    if len(room.members) + 1 >= room.size:
        return web.Response(status=298) # Room is full
    if room.has_started():
        return web.Response(status=299) # Already started
    
    player = GamePlayer(client, body['name'])
    # Quick way to sort new players into different teams
    player.team = room.teams[(len(room.members) + 1) % len(room.teams)]

    room.members.append(player)
    await room.broadcast_update()
    return web.Response(text=dumps({
        'host': room.host and room.host.name,
        'selection': room.selection.mode,
        'medal': room.medal,
        'size': room.size,
        'status': room.loading_status()
    }))
