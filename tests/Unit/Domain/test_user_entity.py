import pytest
from datetime import datetime, timedelta

from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile

def test_user_is_spamming_logic():
    user = User(
        id = 123, 
        first_name = "ABC",
        message_count = 1,
        telegram_profile = TelegramProfile(
            username="new_user_tg",
            language_code="en",
            is_premium=False
        )
    )
    user.last_seen = datetime.now()

    assert user.is_spamming(threshold_seconds = 2)

def test_user_reset_warnings_on_normal_activity():
    user = User(
        id = 123, 
        first_name = "ABC",
        message_count = 2,
        telegram_profile = TelegramProfile(
            username="new_user_tg",
            language_code="en",
            is_premium=False
        )
    )
    user.reset_warnings()
    
    assert user.warnings == 0

def test_user_reaches_mute_limit():
    user = User(
        id = 123, 
        first_name = "ABC",
        message_count = 2,
        warnings = 2,
        telegram_profile = TelegramProfile(
            username="new_user_tg",
            language_code="en",
            is_premium=False
        )
    )

    user.record_spam_activity()
    
    assert user.warnings == 3
    assert user.is_muted is True