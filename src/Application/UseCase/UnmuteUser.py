from src.Domain.Repository.UserRepository import UserRepository

class UnmuteUser:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    
    def execute(self, user_id: int) -> bool:
        user = self.user_repository.find_by_id(user_id)
        if user:
            user.unmute() # Resetea is_muted y warnings
            self.user_repository.save(user)
            return True
        return False
