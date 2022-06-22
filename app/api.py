from fastapi import FastAPI, Request, Form, File, UploadFile, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from peewee import PostgresqlDatabase

from config import POSTGRES_DB
from models import MODELS


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


@app.get("/test")
def teste():
    return {"result": "sucess"}
