import pytest
from unittest.mock import MagicMock

from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile
from src.Application.UseCase.WhitelistUser import WhitelistUser

class TestWhiteListUser:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def use_case(self, user_repository):
        return WhitelistUser(user_repository)

    def test_validate_whitelist_user(self, use_case, user_repository):

        existing_user = User(
            id=1234,
            first_name="whitelist user",
            warnings=0,
            is_muted=False,
            is_whitelisted=False,
            telegram_profile=TelegramProfile(
                username="whitelist",
                is_premium=False,
                language_code="es"
            )
        )

        user_repository.find_by_id.return_value = existing_user

        success = use_case.execute(1234)

        assert success == True
        assert existing_user.is_whitelisted == True

        user_repository.save.assert_called_with(user=existing_user)
