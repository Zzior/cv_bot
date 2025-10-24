from abc import ABC, abstractmethod
from pydantic import BaseModel



class Task(ABC):
    @abstractmethod
    def __init__(self, params: BaseModel) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass