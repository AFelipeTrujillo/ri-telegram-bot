import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile

from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.HandleUserMessage import HandleUserMessage
from src.Infrastructure.Config.Settings import settings

class TestHandleUserMessageIntegration:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()
    
    @pytest.fixture
    def use_case(self, user_repository):
        return HandleUserMessage(user_repository)

    def test_first_message_from_new_user_is_never_spam(self, use_case, user_repository):
        user_repository.find_by_id.return_value = None
        
        dto = UserActivityDTO(
            user_id=999,
            first_name="NewUser",
            username="new_user_tg",
            language_code = "en",
            is_premium = False,
            content = "content",
             has_links = False
        )

        result = use_case.execute(dto)

        assert result == "allow"
        assert user_repository.save.called

        saved_user = user_repository.save.call_args[0][0]
        assert saved_user.id == 999
        assert saved_user.warnings == 0
    
    def test_user_gets_muted_after_three_quick_messages(self, use_case, user_repository):

        existing_user = User(
            id=123, 
            first_name="Spammer", 
            warnings=2,
            message_count=5, # Ya ha enviado mensajes antes
            is_muted=False,
            last_seen=datetime.now(), 
            telegram_profile = TelegramProfile(
                username="new_user_tg",
                language_code="en",
                is_premium=False
            )
        )

        user_repository.find_by_id.return_value = existing_user
        
        dto = UserActivityDTO(
            user_id=123,
            first_name="Spammer",
            username="new_user_tg",
            language_code="en",
            is_premium=False,
            content="mensaje rápido",
            has_links=False
        )
        settings.SPAM_THRESHOLD_SECONDS = 2
        result = use_case.execute( dto = dto)

        assert result == "mute"
        assert existing_user.is_muted is True
        assert existing_user.warnings == 3

        user_repository.save.assert_called_with(existing_user)

    def test_existing_user_updates_profile_data(self, use_case, user_repository):
        
        existing_user = User(
            id = 123, 
            first_name = "Old Name", 
            telegram_profile = TelegramProfile(username="old_tg", language_code="es")
        )
        user_repository.find_by_id.return_value = existing_user
        
        dto = UserActivityDTO(
            user_id = 123,
            first_name = "New Name",
            username = "new_tg",
            language_code = "en",
            has_links = False
        )

        use_case.execute(dto)

        assert existing_user.first_name == "Old Name"
        assert existing_user.profile.username == "new_tg"
        assert existing_user.profile.language_code == "en"
        user_repository.save.assert_called_once()