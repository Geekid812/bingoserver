from aiohttp import web
from json import dumps

from server import GameServer
from room import GamePlayer

async def join_room(request: web.Request):
    body = await request.json()
    server = GameServer.instance()
    client = server.find_client(body['client_secret'])

    if not client:
        # Client is not connected via the TCP port
        return web.Response(status=400)

    room = server.find_room(body['code'])
    if not room:
        return web.Response(status=204) # Room not found
    if len(room.members) + 1 >= room.size:
        return web.Response(status=298) # Room is full
    if room.started:
        return web.Response(status=299) # Already started
    
    player = GamePlayer(client, body['name'])
    # Quick way to sort new players into different teams
    if len(room.members) % 2 == 0: player.team = 1

    room.members.append(player)
    await room.broadcast_update()
    return web.Response(text=dumps({
        'host': room.host.name,
        'selection': room.selection,
        'medal': room.medal,
        'size': room.size
    }))
