import pytest
from unittest.mock import MagicMock
from src.Application.UseCase.HandleUserMessage import HandleUserMessage
from src.Domain.Entity.User import User
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

        result = use_case.execute(
            user_id=999,
            first_name="NewUser",
            username="new_user_tg"
        )

        assert result == "ok"
        assert user_repository.save.called

        saved_user = user_repository.save.call_args[0][0]
        assert saved_user.id == 999
        assert saved_user.warnings == 0
    
    def test_user_gets_muted_after_three_quick_messages(self, use_case, user_repository):

        existing_user = User(
            id=123, 
            first_name="Spammer", 
            warnings=2,
            is_muted=False
        )

        user_repository.find_by_id.return_value = existing_user

        settings.SPAM_THRESHOLD_SECONDS = 2
        result = use_case.execute(user_id=123, first_name="Spammer")

        assert result == "mute"
        assert existing_user.is_muted is True
        assert existing_user.warnings == 3