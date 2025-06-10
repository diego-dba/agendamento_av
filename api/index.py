from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_file = "db.json"

class Agendamento(BaseModel):
    funcionario_id: str
    recurso: str  # 'caixa' ou 'projetor'
    dia: str
    horario: str

def load_db():
    if not os.path.exists(db_file):
        with open(db_file, "w") as f:
            json.dump([], f)
    with open(db_file) as f:
        return json.load(f)

def save_db(data):
    with open(db_file, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/agendar")
async def agendar(data: Agendamento):
    db = load_db()
    limite = 6 if data.recurso == "caixa" else 2
    total = sum(1 for d in db if d["recurso"] == data.recurso and d["dia"] == data.dia and d["horario"] == data.horario)
    if total >= limite:
        raise HTTPException(status_code=400, detail="Limite atingido para este horário")
    db.append(data.dict())
    save_db(db)
    return {"mensagem": "Agendamento realizado com sucesso!"}

@app.get("/agendamentos")
async def listar_agendamentos():
    return load_db()