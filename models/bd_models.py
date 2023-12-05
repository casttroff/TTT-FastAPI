from typing import List, Optional
from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, AutoField
from playhouse.sqlite_ext import JSONField  # Importa JSONField para trabajar con campos JSON

# Usa SqliteDatabase directamente en lugar de db_client
db = SqliteDatabase('sqlite_db.db')

class BaseModel(Model):
    class Meta:
        database = db

class Player(BaseModel):
    name = CharField()
    symbol = CharField()

class StartGame(BaseModel):
    starting_player = CharField()
    players = List[Player]

class InputGame(BaseModel):
    game_id = IntegerField()
    player = CharField()
    row = IntegerField()
    column = IntegerField()

class Game(BaseModel):
    game_id = AutoField(primary_key=True)
    players = JSONField()
    movements_played = IntegerField(default=0)
    next_turn = CharField()
    board = JSONField()
    winner = CharField(null=True)