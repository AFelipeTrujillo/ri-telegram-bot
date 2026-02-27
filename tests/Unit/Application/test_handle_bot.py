import pytest

from unittest.mock import MagicMock
from unittest.mock import patch

from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.FilterBotUnauthorized import FilterBotUnauthorized


class TestHandleBot:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def filter_use_case(self, user_repository):
        return FilterBotUnauthorized(user_repository)


    def test_handle_unknown_bot(self, filter_use_case, user_repository):

        with patch('src.Infrastructure.Config.Settings.settings.BOT_USERNAME', "my_own_bot"):
            dto = UserActivityDTO(
                user_id=888,
                first_name="OtherUserBot",
                username="OtherUserBot"
            )

            decision = filter_use_case.execute(dto= dto, is_bot= True)
            assert decision == "delete"

    def test_handle_known_bot(self, filter_use_case, user_repository):

        with patch('src.Infrastructure.Config.Settings.settings.BOT_USERNAME', "my_own_bot"):
            dto = UserActivityDTO(
                user_id=888,
                first_name="MyOwnBot",
                username="MY_OWN_BOT"
            )

            decision = filter_use_case.execute(dto= dto, is_bot= True)
            assert decision == "allow"

