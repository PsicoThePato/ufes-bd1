from decimal import Decimal
from typing import Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from peewee import PostgresqlDatabase
from pydantic import BaseModel


from config import POSTGRES_DB
from models import MODELS
from models.user import UserController, Err
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
    UserController(PostgresWrapper(POSTGRES_DB)).create_user(user)
    return {"message": "User created!"}


@app.post("/transaction")
def transaction(trans: Transaction):
    status = UserController(PostgresWrapper(POSTGRES_DB)).make_transaction(trans)
    if isinstance(status, Err):
        raise HTTPException(status_code=status.err_status, detail=status.err_message)
    return {"message": "Sucess"}
