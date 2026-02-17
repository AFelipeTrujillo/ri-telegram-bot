from src.Infrastructure.Config.Settings import settings

class HandlePing:

    def execute(self, user_id: int) ->bool:
        return user_id == settings.OWNER_ID
        
