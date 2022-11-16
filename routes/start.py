from aiohttp import web
from json import loads

from server import GameServer

async def start(request: web.Request):
    body = loads(await request.text())
    client_secret = body['client_secret']
    room, player = GameServer.instance().find_player(client_secret)
    if room is None: return web.Response(status=404)
    if not room.host.matches(client_secret): return web.Response(status=403)
    if len(room.maplist) == 0: return web.Response(status=400)
    
    room.started = True
    await room.broadcast_start()
    return web.Response()