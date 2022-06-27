import datetime

from peewee import DecimalField, ForeignKeyField, DateTimeField

from .base import BaseModel
from .user import User


class Transaction(BaseModel):
    value = DecimalField()
    payer = ForeignKeyField(User, field="cpf")
    payee = ForeignKeyField(User, field="cpf")
    date_time = DateTimeField(default=datetime.datetime.now)
