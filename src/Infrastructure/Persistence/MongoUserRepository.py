from pymongo.database import Database

from src.Domain.Entity.User import User
from src.Domain.ValueObject.TelegramProfile import TelegramProfile
from src.Domain.Repository.UserRepository import UserRepository

class MongoUserRepository(UserRepository):

    def __init__(self, db: Database):
        self.collection = db.users

    def find_by_id(self, user_id) -> User:
        
        data = self.collection.find_one({"id": user_id})
        if not data:
            return None
        
        telegram_profile_data = data.get("telegram_profile", {})
        telegram_profile = TelegramProfile(
            username = telegram_profile_data.get("username"),
            language_code = telegram_profile_data.get("language_code"),
            is_premium = telegram_profile_data.get("is_premium", False),
            source = telegram_profile_data.get("source", "organic")
        )
        
        return User(
            id                  = data["id"],
            first_name          = data["first_name"],
            telegram_profile    = telegram_profile,
            is_whitelisted      = data.get("is_whitelisted", False),
            message_count       = data["message_count"],
            warnings            = data.get("warnings", 0),
            is_muted            = data.get("is_muted", False),
            last_seen           = data.get("last_seen"),
            joined_at           = data.get("joined_at")
        )

    def save(self, user: User) -> None:
        self.collection.update_one(
            {"id": user.id},
            { "$set": {
                "first_name"    : user.first_name,
                "telegram_profile" : {
                    "username": user.telegram_profile.username,
                    "language_code": user.telegram_profile.language_code,
                    "is_premium": user.telegram_profile.is_premium,
                    "source": user.telegram_profile.source
                },
                "is_whitelisted" : user.is_whitelisted,
                "message_count" : user.message_count,
                "warnings"      : user.warnings,
                "is_muted"      : user.is_muted,
                "last_seen"     : user.last_seen,
            }},
            upsert = True
        )
