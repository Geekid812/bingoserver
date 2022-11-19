from asyncio import sleep
from aiohttp import web
from json import loads

from server import GameServer

async def claim_cell(request: web.Request):
    body = loads(await request.text())
    room, player = GameServer.instance().find_player(body['client_secret'])
    if room is None: return web.Response(status=404)

    map_uid = body['uid']
    claim_time = body['time']
    claim_medal = body['medal']
    try:
        cellid, claim_map = [(i, m) for i, m in enumerate(room.maplist) if m.uid == map_uid][0]
    except IndexError:
        # Invalid map uid, it should be a map that's not part of the bingo board
        print(f"/claim: invalid map uid {map_uid}. claim time: {claim_time}, claim medal: {claim_medal}. \nmap board: {' '.join([m.uid for m in room.maplist])}")
        await sleep(3000) # Sleep a bit to avoid claim spam from client
        return web.Response()

    if claim_map.time != -1 and claim_map.time <= claim_time: return web.Response(status=204) # Map already claimed

    is_improvement = False
    if claim_map.team == player.team: is_improvement = True

    delta = -1
    if claim_map.team != -1:
        delta = claim_map.time - claim_time

    claim_map.time = claim_time
    claim_map.team = player.team
    claim_map.medal = claim_medal
    await room.broadcast_claim(player, claim_map.name, cellid, claim_time, claim_medal, is_improvement, delta)
    await room.check_winner()
    return web.Response()
