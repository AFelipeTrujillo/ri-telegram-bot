from abc import ABC, abstractmethod
from src.Domain.Entity.User import User

class UserRepository(ABC):

    @abstractmethod
    def find_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

