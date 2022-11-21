from aiohttp import web
from json import loads

from server import GameServer

async def team_update(request: web.Request):
    body = loads(await request.text())
    room, player = GameServer.instance().find_player(body['client_secret'])
    if room is None: return web.Response(status=404)
    if room.has_started() and not room.is_start_intro(): return web.Response(status=406)
    if body['team'] not in ("0", "1"): return web.Response(status=400)

    player.team = int(body['team'])
    await room.broadcast_update()
    return web.Response()
