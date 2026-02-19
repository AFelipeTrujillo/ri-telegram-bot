import pytest
from unittest.mock import patch
from src.Application.UseCase.HandlePing import HandlePing

class TestHandlePing:
    
    @pytest.fixture
    def use_case(self):
        return HandlePing()

    def test_execute_returns_true_for_owner(self, use_case):
        with patch('src.Infrastructure.Config.Settings.settings.OWNER_ID', 12345):
            result = use_case.execute(user_id=12345)
            assert result is True

    def test_execute_returns_false_for_stranger(self, use_case):
        with patch('src.Infrastructure.Config.Settings.settings.OWNER_ID', 12345):
            # Un usuario con ID diferente intenta hacer ping
            result = use_case.execute(user_id=99999)
            assert result is False