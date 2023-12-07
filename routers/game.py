from fastapi import APIRouter, HTTPException, status, Query
from fastapi.exceptions import ResponseValidationError
from models.bd_models import Game
from models.control_models import StartGameModel, InputGameModel, GameModel
from schemas.game_schema import game_starter_schema, game_schema


router = APIRouter(
    prefix="/game",
    tags=["game"],
    responses={400: {"message": "Datos incorrectos."}}
    )


@router.get("/list")
async def games(page: int = Query(1, ge=1), page_size: int = Query(20, le=100), finished: bool = Query(None, description="Filter games by finished status")):
    try:
        # Calcular el índice de inicio y fin para la paginación
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Obtener todos los juegos desde la base de datos
        db_games = Game.select()

        # Filtrar los juegos según el estado (terminado o no)
        if finished is not None:
            db_games = db_games.where(Game.winner.is_null() if not finished else Game.winner.is_null(False))

        # Obtener los juegos para la página actual
        current_page_games = db_games[start_index:end_index]

        # Convertir los juegos a un formato que puedas devolver en la respuesta
        games_list = [{"game_id": game.game_id} for game in current_page_games]

        return games_list

    except Exception as e:
        raise e


@router.get("/list/{id}", status_code=200, response_model=GameModel)
async def get_game(id: int):
    try:
        # Buscar el juego por el ID en la base de datos
        founded_game = Game.get_or_none(Game.game_id == id)
        if founded_game:
            game_dict = game_schema(founded_game)
            return GameModel(**game_dict)
        else:
            raise HTTPException(status_code=404, detail="El ID no fue encontrado")
    except Exception as e:
        raise HTTPException(status_code=404, detail="El ID ya no existe")


@router.post("/start-game", response_model=GameModel)
async def post_query_game(start_game_input: StartGameModel):
    try:
        # Convierte el objeto StartGame a un diccionario
        start_game = game_starter_schema(start_game_input)

        # Crea un nuevo juego usando el diccionario
        new_game = Game.create(**start_game)

        # Obtén el juego recién agregado
        game_started = Game.get(Game.game_id == new_game.game_id)

        game_dict = game_started.__dict__['__data__']

        return GameModel(**game_dict)
    except Exception as e:
        raise(e)
        raise HTTPException(status_code=500, detail="Error accediendo a la base de datos")


@router.post("/play-game", response_model=GameModel)
async def play_game(played_game_input: InputGameModel):
    try:
        founded_game = get_game_or_raise(played_game_input.game_id)
        validate_game_status(founded_game, played_game_input)
        validate_board_position(founded_game, played_game_input.row, played_game_input.column)

        make_move(founded_game, played_game_input.row, played_game_input.column, played_game_input.player)
        winner = GameModel.check_winner(founded_game.board)
        if winner:
            if winner == 'fulled':
                update_winner(founded_game, "Empate")
            else:
                update_winner(founded_game, played_game_input.player)

        return GameModel(**get_updated_game_dict(played_game_input.game_id))

    except IndexError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No existe la posición a la cual quiere insertar datos.")
    except HTTPException as exc:
        raise exc


@router.delete("/delete/{id}", status_code=200)
async def delete_game(id: int):
    try:
        # Buscar el juego por el ID en la base de datos
        game_to_delete = Game.get_or_none(Game.game_id == id)

        if game_to_delete:
            # Eliminar el juego de la base de datos
            game_to_delete.delete_instance()
            return {"message": f"Juego con ID {id} eliminado exitosamente"}

        # Si no se encuentra el juego, lanzar una excepción HTTP 404 Not Found
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    except Exception as e:
        raise e


def get_game_or_raise(game_id: int):
    founded_game = Game.get_or_none(Game.game_id == game_id)
    if not founded_game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el ID del juego.")
    return founded_game


def validate_game_status(game, played_game_input):
    if game.winner is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Este juego ya está terminado. Ganador: {game.winner}.")
    if game.next_turn != played_game_input.player:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Es el turno del jugador '{game.next_turn}'.")


def validate_board_position(game, row, column):
    if game.board[row][column] is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta casilla ya está ocupada.")


def make_move(game, row, column, player):
    player_symbol = get_player_symbol(game, player)
    game.board[row][column] = player_symbol
    game.movements_played += 1
    game.next_turn = get_next_player(game, player)
    game.save()


def update_winner(game, player):
    game.winner = player
    game.save()


def get_updated_game_dict(game_id):
    new_founded_game = Game.get_or_none(Game.game_id == game_id)
    return new_founded_game.__dict__['__data__']


def get_player_symbol(game, player):
    return game.players[0]['symbol'] if game.players[0]['name'] == player else game.players[1]['symbol']


def get_next_player(game, current_player):
    return game.players[1]['name'] if game.players[0]['name'] == current_player else game.players[0]['name']