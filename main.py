import os
import certifi

from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from telegram.ext import ApplicationBuilder, MessageHandler, filters

from src.Application.UseCase.RegisterUserActivity import RegisterUserActivity
from src.Infrastructure.Config.Settings import settings
from src.Infrastructure.Persistence.MongoUserRepository import MongoUserRepository
from src.Infrastructure.Delivery.Http.TelegramController import TelegramController

def main():
    load_dotenv()
    print("Environment variables loaded for ri-telegram-bot.")

    client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    db = client[settings.MONGO_DB_NAME]
    user_repo = MongoUserRepository(db)

    register_use_case = RegisterUserActivity(user_repository=user_repo)

    controller = TelegramController(register_user_case=register_use_case)

    token = settings.TELEGRAM_TOKEN
    app = ApplicationBuilder().token(token = token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), controller.handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
