"""
repository.py
Contrato para persistência de Usuários.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: bytes

class UserRepository(ABC):
    @abstractmethod
    def create(self, email: str, username: str, password_hash: bytes) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def exists(self, email: str, username: str) -> dict:
        pass