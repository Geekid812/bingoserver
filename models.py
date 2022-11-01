from dataclasses import dataclass

class MapSelection:
    TOTD = 0
    RANDOM_TMX = 1

class TargetMedal:
    AUTHOR = 0
    GOLD = 1
    SILVER = 2
    BRONZE = 3

class Team:
    RED = 0
    BLUE = 1

class BingoDirection:
    HORIZONTAL = 1
    VERTICAL = 2
    DIAGONAL = 3

@dataclass
class MapInfo:
    name: str
    author: str
    tmxid: int
    uid: str
    team: int = -1
