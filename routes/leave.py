from aiohttp import web
from json import loads

from server import GameServer

async def leave(request: web.Request):
    body = loads(await request.text())
    client_secret = body['client_secret']
    room, player = GameServer.instance().find_player(client_secret)
    if player is None: return web.Response(status=404)

    await GameServer.instance().remove_client(player.socket)
    
    return web.Response()