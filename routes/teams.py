from aiohttp import web
from json import loads

from server import GameServer

async def team_update(request: web.Request):
    body = loads(await request.text())
    room, player = GameServer.instance().find_player(body['login'])
    if room is None: return web.Response(status=404)
    if player.secret != body['client_secret']: return web.Response(status=405)
    
    player.team = int(body['team'])
    await room.broadcast_update()
    return web.Response()
