from datetime import datetime, timedelta

from src.Domain.Entity.User import User
from src.Application.Factory.UserFactory import UserFactory

from src.Domain.ValueObject.TelegramProfile import TelegramProfile
from src.Domain.Repository.UserRepository import UserRepository
from src.Application.DTO.UserActivityDTO import UserActivityDTO

from src.Infrastructure.Config.Settings import settings

class HandleUserMessage:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, dto: UserActivityDTO) -> str:
        user = self.user_repository.find_by_id(dto.user_id)
        
        if not user:
            user = UserFactory.create_from_dto( dto = dto )
        else :
            user.update_profile(
                username = dto.username,
                language_code = dto.language_code,
                is_premium = dto.is_premium
            )

        if user.is_muted:
            return "mute"
        
        is_spam = user.is_spamming(settings.SPAM_THRESHOLD_SECONDS)
        
        if is_spam:
            user.record_spam_activity()
            user.record_activity()

            self.user_repository.save(user)
            return "mute" if user.warnings >= 3 else "warn"
        
        user.reset_warnings()
        user.record_activity()
        self.user_repository.save(user)
        return "allow"