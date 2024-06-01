from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"info" : "Welcome to EcoMaster!"}

