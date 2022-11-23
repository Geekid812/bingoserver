from aiohttp import web
from json import dumps

from server import GameServer

async def clients_status(request: web.Request):
    server = GameServer.instance()
    return web.Response(text=dumps([
        {
            'token': client.secret,
            'open': client.opened,
            'created': str(client.created)
        }
        for client in server.clients
    ]), content_type='application/json')