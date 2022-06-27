from dataclasses import dataclass
import hashlib
from typing import Any
import re

from peewee import CharField, BooleanField, DecimalField
import requests

from app.api import Transaction

from .base import BaseModel
from .db.base import BaseWrapper


AUTHORIZATION_MOCK = "https://run.mocky.io/v3/8fafdd68-a090-496f-8c9a-3442cf30dae6"
SMS_MOCK = "http://o4d9z.mocklab.io/notify"


@dataclass
class Err:
    err_message: str
    err_status: int


@dataclass
class Success:
    content: Any


class User(BaseModel):
    cpf = CharField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    is_lojista = BooleanField()
    balance = DecimalField()


class UserController:
    def __init__(self, db_wrapper: BaseWrapper) -> None:
        self._db_wrapper = db_wrapper

    def insert_user(self, user: dict):
        placeholder_string = r"%s" + (r", %s" * (len(user) - 1))
        columns = str(tuple(user.keys())).replace("'", "")
        query = f"""INSERT INTO public.user {columns} VALUES ({placeholder_string})"""
        self._db_wrapper.faz_query(
            [
                (
                    query,
                    tuple(user.values()),
                    False,
                )
            ],
            "public",
        )

    def get_user(self, user_cpf: str) -> Err | Success:
        """on success return tuple[bool, str, list[tuple]]"""
        query = r"""SELECT * from public.user where cpf=%s"""
        user = self._db_wrapper.faz_query(
            [
                (
                    query,
                    (self._mask_cpf({"cpf": user_cpf})["cpf"],),
                    True,
                ),
            ],
            "public",
        )
        if not user[0]:
            return Err(f"User {user_cpf} not found", 404)

        return Success(self._parse_user(user[0][0]))

    def _parse_user(self, user: tuple[str, str, str, str, bool]):
        print(f"meu user é: {user}")
        return {
            "cpf": user[0],
            "name": user[1],
            "email": user[2],
            "password": user[3],
            "is_lojista": user[4],
            "balance": user[5],
        }

    def update_users(self, payer: dict, payee: dict, transaction: Transaction):
        # TODO generalizar a função pra dar update em qualquer número de users atomicamente
        query = r"""UPDATE public.user set balance = %s WHERE cpf=%s"""
        constraints_payer = (payer["balance"] - transaction.value, payer["cpf"])
        constraints_payee = (payee["balance"] + transaction.value, payee["cpf"])
        self._db_wrapper.faz_query(
            [
                (query, constraints_payer, False),
                (query, constraints_payee, False),
            ],
            "public",
        )


class UserModel:
    def __init__(self, controller: UserController) -> None:
        self._controller = controller

    def create_user(self, user):
        user = dict(user)
        print(user)
        user = self._validate_user(self._mask_cpf(self._hash_function(user)))
        if isinstance(user, Err):
            return user
        user = user.content
        self._controller.insert_user(
            user,
        )

    def _hash_function(self, user: dict):
        user["password"] = hashlib.sha256(user["password"].encode()).hexdigest()
        return user

    def _mask_cpf(self, user: dict):
        user["cpf"] = "".join([s for s in user["cpf"] if s.isdigit()])
        return user

    def _validate_user(self, user: dict) -> tuple[bool, str]:
        email_regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        if not re.fullmatch(email_regex, user["email"]):
            return Err("Email inválido!", 401)
        if len(user["cpf"]) != 11:
            return Err("CPF inválido!", 401)

        return Success(user)

    def make_transaction(self, transaction: Transaction):
        payer = self._controller.get_user(transaction.payer)
        if isinstance(payer, Err):
            return payer
        print(payer.content)
        payer = payer.content
        if payer["is_lojista"]:
            return Err("Lojistas naõ podem fazer transações", 401)
        if payer["balance"] < transaction.value:
            return Err(f"Usuário {payer['cpf']} não tem saldo o suficiente", 401)

        payee = self._controller.get_user(transaction.payee)
        if isinstance(payee, Err):
            return payee
        payee = payee.content

        is_authorized = requests.get(AUTHORIZATION_MOCK)
        if is_authorized.status_code < 200 or is_authorized.status_code >= 300:
            return Err("Transação não autorizada", is_authorized.status_code)

        send_sms = requests.post(SMS_MOCK)
        if send_sms.status_code < 200 or send_sms.status_code >= 300:
            return Err("Falha no envio do sms", send_sms.status_code)
        return Success(None)
