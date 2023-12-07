from fastapi import FastAPI
from routers import game


app = FastAPI()

app.include_router(game.router)

@app.get("/")
async def root():
    return {"message": "/start-game to start a game :]"}
