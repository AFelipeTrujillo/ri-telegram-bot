
from src.Domain.Entity.User import User
from src.Domain.Repository.UserRepository import UserRepository
from src.Infrastructure.Config.Settings import settings

class ProcessSpamCheck:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, first_name: str, username: str = None):
        
        user = self.user_repository.find_by_id(user_id)
        if not user:
            user = User(id=user_id, first_name=first_name, username=username)
            self.user_repository.save(user)
            return "ok"
        
        if user.is_spamming(settings.SPAM_THRESHOLD_SECONDS):
            user.add_warning()
            user.record_activity()
            self.user_repository.save(user)
        
            if user.warnings >= 3:
                return "mute"
        
            return "warn"
        
        user.reset_warnings()
        user.record_activity()
        self.user_repository.save(user)
        return "ok"


