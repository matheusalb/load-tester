from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from GET!"}

@app.post("/")
async def read_post(item: dict):
    return {"message": "Hello from POST!", "received": item}
