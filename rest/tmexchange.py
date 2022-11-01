import asyncio
import json
from aiohttp import ClientSession

from models import MapSelection, MapInfo

BASE_URL = "https://trackmania.exchange"

class Routes:
    MapSearch = "/mapsearch2/search"

async def get_random_maps(sess: ClientSession, selection: MapSelection, count: int) -> list[MapInfo]:
    url = BASE_URL + Routes.MapSearch
    params = {"api": "on", "random": 1}

    if selection == MapSelection.TOTD:
        params["mode"] = 25
    elif selection == MapSelection.RANDOM_TMX:
        params["mtype"] = "TM_Race"
    else:
        raise ValueError("invalid map selection mode")
    
    maps = []
    async def fetch_map() -> MapInfo:
        async with sess.get(url, params=params) as response:
            if response.status != 200:
                return None
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
    # at a time (up to 5 simultaneously).
    tasks = {fetch_map() for _ in range(min(5, count))}
    reps = 0
    while len(maps) < count:
        if reps > 100:
            # Prevent infinite loop (abort if too many errors)
            raise RuntimeError()

        done, pending = await asyncio.wait(tasks)
        tasks = pending

        for task in done:
            if res := task.result():
                maps.append(res)

        if len(maps) + len(tasks) < count:
            tasks.add(fetch_map())
        reps += 1
    
    return maps