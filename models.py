from dataclasses import dataclass
from gameteam import GameTeam

class MapSelection:
    TOTD = 0
    RANDOM_TMX = 1

class Medal:
    AUTHOR = 0
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    NONE = 4

class BingoDirection:
    HORIZONTAL = 1
    VERTICAL = 2
    DIAGONAL = 3

class LoadStatus:
    LOADING = 0
    LOAD_SUCCESS = 1
    LOAD_FAIL = 2

@dataclass
class MapInfo:
    name: str
    author: str
    tmxid: int
    uid: str
    team: GameTeam = None
    time: int = -1
    medal: Medal = Medal.NONE
