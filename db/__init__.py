from db.client import db_client
from models.bd_models import Game

try:
    # Crea las tablas en la base de datos
    db_client.connect()
    db_client.create_tables([Game])
except Exception as e:
    raise e