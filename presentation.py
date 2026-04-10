from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
app = FastAPI()


@app.get("/users/{id}")
def users(id):
    return {"user_id": id}