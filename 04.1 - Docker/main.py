#criar um codigo que retorna uma mensagem simples para testar o dockerfile
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return "Hello from Dockerized FastAPI!"