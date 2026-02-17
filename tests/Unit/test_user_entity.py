import pytest
from datetime import datetime, timedelta

from src.Domain.Entity.User import User

def test_user_is_spamming_logic():
    user = User(id = 123, first_name = "ABC")
    user.last_seen = datetime.now()

    assert user.is_spamming(threshold_seconds = 2)

def test_user_reset_warnings_on_normal_activity():
    user = User(id = 123, first_name = "ABC", warnings = 2)
    user.reset_warnings()
    
    assert user.warnings == 0

def test_user_reaches_mute_limit():
    user = User(id = 123, first_name = "ABC", warnings = 2)
    user.record_spam_activity()
    
    assert user.warnings == 3
    assert user.is_muted is True