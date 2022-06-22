import datetime

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    BooleanField,
    DecimalField,
)


class BaseModel(Model):
    class Meta:
        legacy_table_names = False


class User(BaseModel):
    cpf = CharField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    is_lojista = BooleanField()


class Transaction(BaseModel):
    value = DecimalField()
    payer = ForeignKeyField(User, field="cpf")
    payee = ForeignKeyField(User, field="cpf")
    date_time = DateTimeField(default=datetime.datetime.now)
