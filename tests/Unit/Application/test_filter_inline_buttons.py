import pytest
from unittest.mock import patch
from unittest.mock import MagicMock

from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.FilterInlineButtons import FilterInlineButtons

class TestFilterInlineButtons:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def filter_use_case(self, user_repository):
        return FilterInlineButtons(user_repository)
    
    def test_delete_message_when_contains_inline_buttons_and_user_is_not_admin(self, filter_use_case):
        
        dto = UserActivityDTO(
            user_id     =888,
            first_name  ="AdminUser",
            has_links   =True,
            has_inline_buttons = True
        )
        
        result = filter_use_case.execute(dto, is_admin=False)

        assert result == "delete"

    def test_allow_inline_buttons_if_user_is_admin(self, filter_use_case):

        dto = UserActivityDTO(user_id=123, first_name="Admin", has_inline_buttons=True)

        result = filter_use_case.execute(dto, is_admin=True)

        assert result == "allow"