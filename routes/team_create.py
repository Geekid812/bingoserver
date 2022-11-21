from aiohttp import web
from json import loads
import random

from config import MAX_ROOM_TEAM_COUNT
from server import GameServer
from gameteam import GameTeam

async def team_create(request: web.Request):
    body = loads(await request.text())
    client_secret = body['client_secret']
    room, player = GameServer.instance().find_player(client_secret)
    if room is None: return web.Response(status=404)
    if not room.host.matches(client_secret): return web.Response(status=403)
    
    if len(room.teams) >= MAX_ROOM_TEAM_COUNT: return web.Response(status=298)
    
    available_colors = [color_entry for color_entry in GameTeam.colors.items() if color_entry[1] not in [team.color for team in room.teams]]
    color = random.choice(available_colors)
    new_team = GameTeam(max(map(lambda t: t.id, room.teams)) + 1, color[0], color[1])
    
    room.teams.append(new_team)
    await room.broadcast_update()
    return web.Response()