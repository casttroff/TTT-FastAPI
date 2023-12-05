import pytest
from peewee import SqliteDatabase
from models.bd_models import Player, StartGame, InputGame, Game
from schemas.game_schema import game_schema
import sys
import os

# Añade la ruta a la carpeta que contiene main.py al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)
@pytest.fixture
def db():
    # Configura la base de datos de memoria para las pruebas
    test_db = SqliteDatabase(':memory:')
    test_db.connect()
    test_db.create_tables([Player, StartGame, InputGame, Game])

    yield test_db

    # Cierra la conexión de la base de datos después de las pruebas
    test_db.close()

def test_create_player(db):
    player = Player.create(name='Alice', symbol='X')
    assert player.name == 'Alice'
    assert player.symbol == 'X'

def test_create_start_game(db):
    start_game = StartGame.create(starting_player='Alice', players=[Player(name='Alice', symbol='X')])
    assert start_game.starting_player == 'Alice'
    assert start_game.players[0].name == 'Alice'
    assert start_game.players[0].symbol == 'X'

def test_create_input_game(db):
    input_game = InputGame.create(game_id=1, player='Alice', row=2, column=3)
    assert input_game.game_id == 1
    assert input_game.player == 'Alice'
    assert input_game.row == 2
    assert input_game.column == 3

def test_create_game(db):
    game = Game.create(players=[{'name': 'Alice', 'symbol': 'X'}, {'name': 'Bob', 'symbol': 'O'}],
                       movements_played=0, next_turn='Alice', board=[], winner=None)
    assert game.players[0]['name'] == 'Alice'
    assert game.players[0]['symbol'] == 'X'
    assert game.movements_played == 0
    assert game.next_turn == 'Alice'
    assert game.board == []
    assert game.winner is None

game_data = {
    "players": [
        {"name": "Player1", "symbol": "X"},
        {"name": "Player2", "symbol": "O"}
    ],
    "starting_player": "Player1"
}

# Fixture to create a game for testing
@pytest.fixture
def create_test_game():
    game = Game.create(**game_data)
    return game

def test_get_games():
    response = client.get("/game/list")
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_get_game(create_test_game):
    game_id = create_test_game.game_id
    response = client.get(f"/game/list/{game_id}")
    assert response.status_code == 200
    assert response.json() == game_schema(create_test_game)

def test_get_nonexistent_game():
    response = client.get("/game/list/999")
    assert response.status_code == 200
    assert response.json() == {"message": "El ID es inválido"}