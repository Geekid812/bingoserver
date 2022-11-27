import asyncio
import json
import traceback
import random
from aiohttp import ClientSession

from models import MapSelection, MapMode, MapInfo

BASE_URL = "https://trackmania.exchange"

class Routes:
    MapSearch = "/mapsearch2/search"
    MappackMaps = "/api/mappack/get_mappack_tracks/"

async def get_random_maps(sess: ClientSession, selection: MapSelection, count: int) -> list[MapInfo]:
    url = BASE_URL + Routes.MapSearch
    params = {"api": "on", "random": 1}

    if selection.mode == MapMode.TOTD:
        params["mode"] = 25
    elif selection.mode == MapMode.RANDOM_TMX:
        params["mtype"] = "TM_Race"
        params["etags"] = "23,37,40"
        params["vehicles"] = "1"
    elif selection.mode == MapMode.MAPPACK:
        return await get_maps_from_mappack(sess, count, selection.mappack_id)
    else:
        raise ValueError("invalid map selection mode")
    
    maps = []
    SERVER_ERROR = 0 # Identifiable constant
    async def fetch_map() -> MapInfo:
        async with sess.get(url, params=params) as response:
            if response.status != 200:
                return SERVER_ERROR
            data = json.loads(await response.text())
            mapinfo = data["results"][0]

            # Prevent duplicates
            if mapinfo["TrackID"] in [map_.tmxid for map_ in maps]:
                return None

            return MapInfo(
                tmxid=mapinfo["TrackID"],
                uid=mapinfo["TrackUID"],
                name=mapinfo["Name"],
                author=mapinfo["Username"]
            )
    
    # Create a pool that fetches random maps one request
    # at a time (up to 3 simultaneously).
    tasks = {fetch_map() for _ in range(min(3, count))}
    reps = 0
    while len(maps) < count:
        if reps > 100:
            # Prevent infinite loop (abort if too many errors)
            return maps

        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            tasks = pending

            error = False
            for task in done:
                if res := task.result():
                    maps.append(res)
                elif res == SERVER_ERROR:
                    error = True
                    break

            if error: break
            if len(maps) + len(tasks) < count:
                tasks.add(fetch_map())
        except Exception as e:
            traceback.print_exception(e)
            break
        reps += 1
    
    return maps

async def get_maps_from_mappack(sess: ClientSession, count: int, mappack_id: str) -> list[MapInfo]:
    url = BASE_URL + Routes.MappackMaps + mappack_id

    async with sess.get(url) as response:
        if response.status != 200:
            return []
        try:
            data = json.loads(await response.text())
        except json.decoder.JSONDecodeError:
            return []

        try:
            maps = [
                MapInfo(
                    tmxid=mapinfo["TrackID"],
                    uid=mapinfo["TrackUID"],
                    name=mapinfo["Name"],
                    author=mapinfo["Username"]
                ) for mapinfo in data
            ]
            if len(maps) < count: return maps
            return random.sample(maps, k=count)
        except:
            return []
