import asyncio
from aiohttp import web

import routes
from config import TCP_LISTEN_PORT, HTTP_LISTEN_PORT
from client import ClientTCPSocket
from server import GameServer
from auth import authenticate

async def on_client_connection(reader, writer):
    server = GameServer.instance()
    server.clients.append(ClientTCPSocket(server, reader, writer))

async def main():
    asyncio.create_task(asyncio.start_server(on_client_connection, port=TCP_LISTEN_PORT))

    app = web.Application(middlewares=[authenticate])
    app.add_routes([
        web.post('/create', routes.create),
        web.post('/join', routes.join_room),
        web.post('/team-update', routes.team_update),
        web.post('/start', routes.start),
        web.post('/claim', routes.claim_cell),
        web.post('/sync', routes.sync_client),

        # Private routes
        web.get('/internal/rooms', routes.rooms_status),
        web.get('/internal/clients', routes.clients_status)
    ])
    return app

web.run_app(main(), port=HTTP_LISTEN_PORT)
