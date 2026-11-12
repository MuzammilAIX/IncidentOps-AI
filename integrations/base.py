
from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def health_check(self) -> bool: ...

    @abstractmethod
    def get_status(self, service_id: str) -> dict: ...
