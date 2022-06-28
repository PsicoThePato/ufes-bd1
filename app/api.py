from decimal import Decimal
from typing import Optional
import json

from fastapi import FastAPI, HTTPException
from peewee import PostgresqlDatabase
from pydantic import BaseModel

from config import POSTGRES_DB
from models import MODELS
from models.user import UserController, Err, UserModel
from models.db.postgres import PostgresWrapper


class User(BaseModel):
    cpf: str
    name: str
    email: str
    password: str
    is_lojista: bool
    balance: Optional[Decimal]


class Transaction(BaseModel):
    value: Decimal
    payer: str
    payee: str


app = FastAPI(
    title="API BD - PicPay Challenge",
    description="Primeiro trabalho da disciplina de BD",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup():
    peewee_database = PostgresqlDatabase(
        POSTGRES_DB.db_name,
        user=POSTGRES_DB.user,
        password=POSTGRES_DB.password,
        host=POSTGRES_DB.host,
        port=POSTGRES_DB.port,
    )
    peewee_database.bind(MODELS)
    peewee_database.connect
    peewee_database.create_tables(MODELS)
    peewee_database.close()


@app.get("/health")
def healthcheck():
    return {"result": "sucess"}


@app.post("/create-user")
def create_user(user: User):
    """Cria um usuário no banco de dados"""
    UserModel(UserController(PostgresWrapper(POSTGRES_DB))).create_user(user)
    return {"message": "User created!"}


@app.post("/transaction")
def transaction(trans: Transaction):
    """Faz uma transação entre usuário não lojista e usuário no sistema"""
    status = UserModel(UserController(PostgresWrapper(POSTGRES_DB))).make_transaction(trans)
    if isinstance(status, Err):
        raise HTTPException(status_code=status.err_status, detail=status.err_message)
    return {"message": "Sucess"}


@app.get("/users/{cpf}")
async def get_user(cpf: str):
    """Retorna as informações de um usuário, buscando-o pelo seu cpf"""
    user = UserModel(UserController(PostgresWrapper(POSTGRES_DB))).get_user(cpf)
    if isinstance(user, Err):
        raise HTTPException(status_code=user.err_status, detail=user.err_message)
    user.content["balance"] = str(user.content["balance"])
    return json.dumps(user.content)
