from peewee import SqliteDatabase
from models.bd_models import Game

# Conecta a la base de datos SQLite (puedes cambiar el nombre del archivo según tus necesidades)
db_client = SqliteDatabase('sqlite_db.db')

try:
    # Crea las tablas en la base de datos
    db_client.connect()
    db_client.create_tables([Game])
except Exception as e:
    raise e