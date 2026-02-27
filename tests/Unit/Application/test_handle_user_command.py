import pytest
from datetime import datetime

from unittest.mock import MagicMock

from src.Domain.Entity.User import User
from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.HandleUserCommand import HandleUserCommand
from src.Domain.ValueObject.TelegramProfile import TelegramProfile


class TestHandleUserCommand:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def filter_use_case(self, user_repository):
        return HandleUserCommand(user_repository)

    def test_admin_send_command(self, filter_use_case, user_repository):

        dto = UserActivityDTO(
            user_id=888,
            first_name="AdminUser",
            username="AdminUser"
        )

        is_admin = True
        has_command = True
        result = filter_use_case.execute(dto=dto, is_admin=is_admin, has_command=has_command)

        assert result == "allow"

    def test_other_user_send_command_and_mute(self, filter_use_case, user_repository):

        existing_user = User(
            id=123,
            first_name="Spammer",
            warnings=2,
            message_count=5,
            is_muted=False,
            last_seen=datetime.now(),
            telegram_profile=TelegramProfile(
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

        is_admin = False
        has_command = True
        result = filter_use_case.execute(dto=dto, is_admin=is_admin, has_command=has_command)

        assert result == "mute"
        assert existing_user.is_muted is True

    def test_other_user_send_command_and_delete(self, filter_use_case, user_repository):

        existing_user = User(
            id=123,
            first_name="Spammer",
            warnings=0,
            message_count=5,
            is_muted=False,
            last_seen=datetime.now(),
            telegram_profile=TelegramProfile(
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

        is_admin = False
        has_command = True
        result = filter_use_case.execute(dto=dto, is_admin=is_admin, has_command=has_command)

        assert result == "delete"
        assert existing_user.is_muted is False