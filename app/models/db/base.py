from abc import ABC, abstractmethod

from config.settings import ApiDB


query = str
schema = str
constraints = tuple
select = bool


class BaseWrapper(ABC):
    connection_params: ApiDB

    @abstractmethod
    def faz_query(
        self, transactions: list[tuple[query, schema, constraints, select]]
    ) -> list[list[tuple]]:
        """DO NOT change the function type"""


# why is python's type system so incredibly shit?
