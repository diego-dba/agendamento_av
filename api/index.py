from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve os arquivos estáticos da pasta "public"
app.mount("/static", StaticFiles(directory="public"), name="static")

DB_PATH = os.path.join(os.path.dirname(__file__), "../db.json")

class Agendamento(BaseModel):
    funcionario_id: str
    recurso: str  # 'caixa' ou 'projetor'
    dia: str
    horario: str

def carregar_dados():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump([], f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DB_PATH, "w") as f:
        json.dump(dados, f, indent=2)

@app.post("/api/agendar")
async def agendar(dado: Agendamento):
    dados = carregar_dados()
    limite = 6 if dado.recurso == "caixa" else 2
    conflitos = [a for a in dados if a["dia"] == dado.dia and a["horario"] == dado.horario and a["recurso"] == dado.recurso]

    if len(conflitos) >= limite:
        raise HTTPException(status_code=400, detail="Limite atingido para esse horário.")

    dados.append(dado.dict())
    salvar_dados(dados)
    return {"mensagem": "Agendamento realizado com sucesso!"}

@app.get("/api/agendamentos")
async def listar():
    return carregar_dados()

# Rota para servir o index.html na raiz "/"
@app.get("/", response_class=HTMLResponse)
async def raiz():
    caminho = os.path.join("public", "index.html")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()
