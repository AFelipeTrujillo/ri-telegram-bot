from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Domain.Repository.UserRepository import UserRepository
from src.Infrastructure.Config.Settings import settings

class FilterBotUnauthorized:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, dto: UserActivityDTO, is_bot: bool) -> str:

        if is_bot:
            if dto.username.lower() != settings.BOT_USERNAME.lower():
                return "delete"

        return "allow"