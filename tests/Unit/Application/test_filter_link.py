import pytest
from unittest.mock import patch
from unittest.mock import MagicMock

from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.FilterLink import FilterLink

class TestFilterLink:

    @pytest.fixture
    def user_repository(self):
        return MagicMock()

    @pytest.fixture
    def filter_use_case(self, user_repository):
        return FilterLink(user_repository)
    
    def test_admin_can_send_links_without_sanction(self, filter_use_case, user_repository):
        
        dto = UserActivityDTO(
            user_id=888,
            first_name="AdminUser",
            has_links=True
        )
        
        result = filter_use_case.execute(dto, is_admin=True)

        assert result == "allow"
        assert not user_repository.save.called