from src.Domain.Entity.User import User
from src.Infrastructure.Config.Settings import settings

class FilterLink:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def execute(self, user_id: int, first_name: str, has_entities: bool, is_admin: bool) -> str:

        if user_id == settings.OWNER_ID or is_admin:
            return "allow"
        
        if not has_entities:
            return "allow"
        
        user = self.user_repository.find_by_id(user_id)
        if not user:
            user = User(id=user_id, first_name=first_name)
        
        user.record_link_violation()
        self.user_repository.save(user)

        if user.is_muted:
            return "mute_and_delete"
        
        return "delete"
        
