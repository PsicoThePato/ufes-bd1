from abc import ABC, abstractmethod

from config.settings import ApiDB


class BaseWrapper(ABC):
    connection_params: ApiDB

    @abstractmethod
    def faz_query(
        self, query: str, schema: str, constraints_tuple: tuple = None, select: bool = False
    ) -> list[tuple]:
        """abstract"""


# why is python's type system so incredibly shit?
