
from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile
from src.Application.DTO.UserActivityDTO import UserActivityDTO

class UserFactory:

    @staticmethod
    def create_from_dto(dto: UserActivityDTO) -> User:

        telegram_profile = TelegramProfile(
            username = dto.username,
            language_code = dto.language_code,
            is_premium = dto.is_premium,
            source = dto.source 
        )

        return User(
            id = dto.user_id, 
            first_name = dto.first_name,
            telegram_profile = telegram_profile,
            is_whitelisted = False
        )
