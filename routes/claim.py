from aiohttp import web
from json import loads

from server import GameServer

async def claim_cell(request: web.Request):
    body = loads(await request.text())
    room, player = GameServer.instance().find_player(body['login'])
    if room is None: return web.Response(status=404)

    map_uid = body['uid']
    cellid, claim_map = [(i, m) for i, m in enumerate(room.maplist) if m.uid == map_uid][0]

    if claim_map.team != -1: return web.Response(status=204) # Map already claimed

    claim_map.team = player.team
    await room.broadcast_claim(player, claim_map.name, cellid)
    await room.check_winner()
    return web.Response()
