from aiohttp import web

from server import GameServer

async def start(request: web.Request):
    login = await request.text()
    room, player = GameServer.instance().find_player(login)
    if room is None: return web.Response(status=404)
    if not room.host.matches(login): return web.Response(status=403)

    room.started = True
    await room.broadcast_start()
    return web.Response()