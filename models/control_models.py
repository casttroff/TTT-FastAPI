from pydantic import BaseModel, validator, ValidationInfo, ValidationError
from typing import List, Optional

class PlayerModel(BaseModel):
    name: str
    symbol: str

    class Config:
        extra = "forbid"

class StartGameModel(BaseModel):
    players: List[PlayerModel]
    starting_player: str

    class Config:
        extra = "forbid"

    @validator("players")
    def validate_players(cls, value):
        # Verificar que hayan dos jugadores en players y que los nombres sean distintos
        if len(value) != 2:
            raise ValueError("El input players debe tener exactamente 2 elementos.")
        
        if value[0].name == value[1].name:
            raise ValueError("Los nombres de los jugadores deben ser diferentes.")

        if value[0].symbol == value[1].symbol:
            raise ValueError("Los símbolos de los jugadores deben ser diferentes.")
        
        return value
    
    @validator("starting_player")
    def validate_starting_player(cls, value, values):
        # Verificar que starting_player sea igual al nombre de uno de los jugadores
        if values.get("players") is not None:
            player_names = [player.name for player in values.get("players")]
            if value not in player_names:
                raise ValueError("starting_player debe ser igual al nombre de uno de los jugadores.")
            
            return value
    
class InputGameModel(BaseModel):
    game_id: int
    player: str
    row: int
    column: int

    class Config:
        extra = "forbid"


class GameModel(BaseModel):
    game_id: int
    players: List[PlayerModel]
    movements_played: int = 0
    next_turn: str
    board: List[List[Optional[str]]]
    winner: Optional[str]

    class Config:
        extra = "forbid"

    @classmethod
    def check_winner(cls, board):
        # Verificar filas y columnas
        for i in range(3):
            if all(board[i][j] == board[i][0] for j in range(3)) and board[i][0] is not None:
                print(f"Ganador en la fila {i}")
                return board[i][0]  
            if all(board[j][i] == board[0][i] for j in range(3)) and board[0][i] is not None:
                print(f"Ganador en la columna {i}")
                return board[0][i]

        # Verificar diagonales
        if all(board[i][i] == board[0][0] for i in range(3)) and board[0][0] is not None:
            print(f"Ganador en la diagonal principal")
            return board[0][0]

        if all(board[i][2 - i] == board[0][2] for i in range(3)) and board[0][2] is not None:
            print(f"Ganador en la diagonal inversa")
            return board[0][2]
        
        # Verificar si el tablero está lleno
        if all(all(cell is not None for cell in row) for row in board):
            return "fulled"
        
        return None  # No hay ganador