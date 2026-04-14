from fastapi import FastAPI
app = FastAPI()


@app.get("/users/{id}")
def users(id):
    return {"user_id": id}



wse
s
def