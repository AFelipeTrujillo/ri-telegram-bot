from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile

from src.Application.Factory.UserFactory import UserFactory
from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Domain.Repository.UserRepository import UserRepository

from src.Infrastructure.Config.Settings import settings

class FilterLink:

    def __init__(self, user_repository: UserRepository):
        self.user_repository : UserRepository = user_repository

    def execute(self, dto: UserActivityDTO, is_admin: bool) -> str:

        if dto.user_id == settings.OWNER_ID or is_admin:
            return "allow"
        
        if not dto.has_links:
            return "allow"
        
        user = self.user_repository.find_by_id(dto.user_id)
        
        if not user:
            user = UserFactory.create_from_dto(dto = dto)
        else:
            user.update_profile(
                username = dto.username,
                language_code = dto.language_code,
                is_premium = dto.is_premium 
            )
        
        user.record_link_violation()
        self.user_repository.save(user)

        if user.is_muted:
            return "mute_and_delete"
        
        return "delete"
        
