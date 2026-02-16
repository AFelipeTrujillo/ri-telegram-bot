from pymongo.database import Database

from src.Domain.Entity.User import User
from src.Domain.Repository.UserRepository import UserRepository

class MongoUserRepository(UserRepository):

    def __init__(self, db: Database):
        self.collection = db.users

    def find_by_id(self, user_id) -> User:
        
        data = self.collection.find_one({"id": user_id})
        if not data:
            return None
        
        return User(
            id = data["id"],
            username = data["username"],
            first_name = data["first_name"],
            message_count = data["message_count"],
            last_seen = data["last_seen"]
        )

    def save(self, user: User) -> None:
        self.collection.update_one(
            {"id": user.id},
            { "$set": {
                "username" : user.username,
                "first_name" : user.first_name,
                "message_count" : user.message_count,
                "last_seen" : user.last_seen
            }},
            upsert = True
        )
