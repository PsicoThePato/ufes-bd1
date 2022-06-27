import hashlib
import json
import re

from peewee import CharField, BooleanField

from .base import BaseModel
from .db.base import BaseWrapper


class User(BaseModel):
    cpf = CharField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    is_lojista = BooleanField()


class UserController:
    def __init__(self, db_wrapper: BaseWrapper) -> None:
        self._db_wrapper = db_wrapper

    def create_user(self, user):
        user = dict(user)
        print(user)
        user = self._mask_cpf(self._hash_function(user))
        is_valid, err = self._validate_user(user)
        if not is_valid:
            raise AssertionError(err)

        self._insert_user(
            user,
            self._db_wrapper,
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
            return (False, "Email inválido!")
        if len(user["cpf"]) != 11:
            return (False, "Cpf inválido")
        return True, ""

    def _insert_user(self, user: dict, db_wrapper: BaseWrapper):
        placeholder_string = r"%s" + (r", %s" * (len(user) - 1))
        columns = str(tuple(user.keys())).replace("'", "")
        query = f"""INSERT INTO public.user {columns} VALUES ({placeholder_string})"""
        db_wrapper.faz_query(query, "public", tuple(user.values()))
