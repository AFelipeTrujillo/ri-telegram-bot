
from src.Domain.Repository.UserRepository import UserRepository

class WhitelistUser:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    

    def execute(self, target_user_id: int) -> bool:

        user = self.user_repository.find_by_id(
            user_id = target_user_id
        )

        if not user:
            return False

        user.toggle_whitelist(True)
        self.user_repository.save(user = user)
        return True