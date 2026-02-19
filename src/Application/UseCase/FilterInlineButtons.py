
from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Infrastructure.Config.Settings import settings

class FilterInlineButtons:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, dto : UserActivityDTO, is_admin: bool):

        if is_admin or dto.user_id == settings.OWNER_ID:
            return "allow"
        
        if dto.has_inline_buttons:
            return "delete"

        return "allow"
        

