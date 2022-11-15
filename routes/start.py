from aiohttp import web
from json import loads

from server import GameServer

async def start(request: web.Request):
    body = loads(await request.text())
    login = body['login']
    room, player = GameServer.instance().find_player(login)
    if room is None: return web.Response(status=404)
    if player.secret != body['client_secret']: return web.Response(status=405)
    if not room.host.matches(login): return web.Response(status=403)

    room.started = True
    await room.broadcast_start()
    return web.Response()