from typing import Optional

from src.Domain.Repository.UserRepository import UserRepository
from src.Domain.Entity.User import User

class RegisterUserActivity:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, first_name: str, username: Optional[str] = None):

        user = self.user_repository.find_by_id(user_id=user_id)
        if not user:
            user = User(
                id = user_id,
                first_name = first_name,
                username = username
            )
        else:
            user.first_name = first_name
            user.username = username
        
        user.record_activity()
        self.user_repository.save(user=user)
