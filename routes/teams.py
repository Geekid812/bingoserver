from aiohttp import web
from json import loads
import random

from server import GameServer
from config import MAX_ROOM_TEAM_COUNT
from gameteam import GameTeam


async def team_update(request: web.Request):
    body = loads(await request.text())
    room, player = GameServer.instance().find_player(body['client_secret'])
    if room is None: return web.Response(status=404)
    if room.has_started() and not room.is_start_intro(): return web.Response(status=406)
    if body['team_id'] not in map(lambda t: t.id, room.teams): return web.Response(status=400)
    
    player.team = room.find_team(int(body['team_id']))
    await room.broadcast_update()
    return web.Response()

async def team_create(request: web.Request):
    body = loads(await request.text())
    client_secret = body['client_secret']
    room, player = GameServer.instance().find_player(client_secret)
    if room is None: return web.Response(status=404)
    if not room.host or not room.host.matches(client_secret): return web.Response(status=403)
    if len(room.teams) >= MAX_ROOM_TEAM_COUNT: return web.Response(status=298)
    
    available_colors = [color_entry for color_entry in GameTeam.colors.items() if color_entry[1] not in [team.color for team in room.teams]]
    color = random.choice(available_colors)
    new_team = GameTeam(max(map(lambda t: t.id, room.teams)) + 1, color[0], color[1])
    
    room.teams.append(new_team)
    await room.broadcast_update()
    return web.Response()