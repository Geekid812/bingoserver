import asyncio
from aiohttp import web

import routes
from config import TCP_LISTEN_PORT, HTTP_LISTEN_PORT
from client import ClientTCPSocket
from server import GameServer

async def on_client_connection(reader, writer):
    server = GameServer.instance()
    server.clients.append(ClientTCPSocket(server, reader, writer))

async def main():
    asyncio.create_task(asyncio.start_server(on_client_connection, port=TCP_LISTEN_PORT))

    app = web.Application()
    app.add_routes([
        web.post('/create', routes.create),
        web.post('/join', routes.join_room),
        web.post('/team-update', routes.team_update),
        web.post('/start', routes.start),
        web.post('/claim', routes.claim_cell),
        # web.get('/rooms', routes.rooms_status)
    ])
    return app

web.run_app(main(), port=HTTP_LISTEN_PORT)
