from models.control_models import PlayerModel, GameModel


def game_starter_schema(game_starter) -> dict:
    return {
        "players": [player_dict_schema(player) for player in game_starter.players],
        "movements_played": 0,
        "next_turn": game_starter.starting_player,
        "board": [[None, None, None], [None, None, None], [None, None, None]],
        "winner": None
    }

def game_schema(game: GameModel) -> dict:
    return {
                "game_id": game.game_id,
                "players": [{"name": player['name'], "symbol": player['symbol']} for player in game.players],
                "movements_played": game.movements_played,
                "next_turn": game.next_turn,
                "board": game.board,
                "winner": game.winner
    }

def player_dict_schema(player: PlayerModel) -> dict:
    return {
        "name": player.name,
        "symbol": player.symbol,
    }