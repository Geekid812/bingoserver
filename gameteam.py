class GameTeam:
    colors = {'Red': (1, 0, 0), 'Blue': (0, 0, 1), 'Green': (0, 1, 0), 'Yellow': (1, 1, 0), 'Pink': (1, 0, 1), 'Cyan': (0, 1, 1)}
    
    def __init__(self, id: int, name: str, color: tuple[float, float, float]):
        self.id = id
        self.name = name
        self.color = color
        
    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, GameTeam) and self.id == __o.id