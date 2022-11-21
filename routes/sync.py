from aiohttp import web
from json import dumps
from datetime import datetime

from server import GameServer

async def sync_client(request: web.Request):
    body = await request.json()
    previous_secret = body['reconnect']
    client_secret = body['client_secret']

    server = GameServer.instance()
    client = server.find_client(client_secret)

    if not client:
        # Client is not connected via the TCP port
        return web.Response(status=400)

    room, player = server.find_player(previous_secret)
    if room is None:
        return web.Response(status=204)
    
    # Swap old and new client connections
    old_client = player.socket
    old_client.closed = True
    player.socket = client
    await server.remove_client(old_client)

    return web.Response(text=dumps({
        'host': room.host.name,
        'selection': room.selection,
        'medal': room.medal,
        'size': room.size,
        'status': room.loading_status(),
        'started': (int((datetime.utcnow().timestamp() - room.started.timestamp()) * 1000) if room.started is not None else -1),
        'teams': [
            {
                'id': team.id,
                'name': team.name,
                'color': {
                    'r': team.color[0],
                    'g': team.color[1],
                    'b': team.color[2]
                }
            }
            for team in room.teams
        ],
        'players': [
            {
                'name': player.name,
                'team': player.team,
            }
            for player in (room.members + [room.host])
        ],
        'boardstate': ([] if not room.started else [
            {
                'name': gamemap.name,
                'author': gamemap.author,
                'tmxid': gamemap.tmxid,
                'uid': gamemap.uid,
                'claim': (None if gamemap.time == -1 else {
                    'team_id': gamemap.team,
                    'time': gamemap.time,
                    'medal': gamemap.medal
                })
            }
            for gamemap in room.maplist
        ])
    }))
