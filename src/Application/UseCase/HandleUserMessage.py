from datetime import datetime, timedelta
from src.Domain.Entity.User import User
from src.Domain.Repository.UserRepository import UserRepository
from src.Infrastructure.Config.Settings import settings

class HandleUserMessage:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, first_name: str, username: str = None) -> str:
        user = self.user_repository.find_by_id(user_id)
        
        if not user:
            past_date = datetime.now() - timedelta(minutes=1)
            user = User(
                id=user_id, 
                first_name=first_name, 
                username=username,
                last_seen=past_date
            )
            user.record_activity() # Primer mensaje
            self.user_repository.save(user)
            return "ok"

        is_spam = user.is_spamming(settings.SPAM_THRESHOLD_SECONDS)

        user.first_name = first_name
        user.username = username
        
        if is_spam:
            user.add_warning()
            user.record_activity()

            self.user_repository.save(user)
            return "mute" if user.warnings >= 3 else "warn"
        
        user.reset_warnings()
        user.record_activity()
        self.user_repository.save(user)
        return "ok"