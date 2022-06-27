import psycopg2

from config.settings import ApiDB
from .base import BaseWrapper


class PostgresWrapper(BaseWrapper):
    def __init__(self, connection_params: ApiDB) -> None:
        self.connection_params = connection_params

    def faz_query(
        self, transactions: list[tuple[str, str, tuple, bool]], schema: str
    ) -> list[list[tuple]]:
        """
        Recebe uma query e, opcionalmente, uma tupla de constraints
        e um parâmetro para retornar o resultado da query.
        A query precisa estar nos padrões especificados na biblioteca Psycopg2:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
                Args:
                    query: Uma string contendo a query postgresql a ser realizada
                    constraints_tuple: Valores que serão substituidos
                                        pelos placeholders na query
                    select: Um booleano para decidir se haverá um retorno
                            das linhas selecionadas
                Returns:
                    None caso select seja falso, e as linhas selecionadas
                    pela query caso contrário
        """

        lista_select = []
        with psycopg2.connect(
            dbname=self.connection_params.db_name,
            user=self.connection_params.user,
            password=self.connection_params.password,
            host=self.connection_params.host,
            port=self.connection_params.port,
            options="-c search_path=" + schema,
        ) as conn:
            cur = conn.cursor()
            for transaction in transactions:
                query = transaction[0]
                constraints_tuple = transaction[1]
                select = transaction[2]
                print(f"Minha query é: {cur.mogrify(query)}")
                if not constraints_tuple:
                    cur.execute(query)
                else:
                    cur.execute(query, constraints_tuple)
                if select:
                    lista_select.append(cur.fetchall())
            conn.commit()
            cur.close()

        return lista_select
