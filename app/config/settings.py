from os import getenv


class ApiDB:
    db_name: str = getenv("POSTGRES_DB")
    user: str = getenv("POSTGRES_USER")
    password: str = getenv("POSTGRES_PASSWORD")
    host: str = getenv("POSTGRES_HOST")
    port: str = getenv("POSTGRES_PORT")


POSTGRES_DB = ApiDB()
