import os
import certifi

from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from telegram.ext import ApplicationBuilder, MessageHandler, filters

#Use Cases
from src.Application.UseCase.RegisterUserActivity import RegisterUserActivity
from src.Application.UseCase.ProcessSpamCheck import ProcessSpamCheck
from src.Application.UseCase.HandleUserMessage import HandleUserMessage

from src.Infrastructure.Config.Settings import settings
from src.Infrastructure.Persistence.MongoUserRepository import MongoUserRepository
from src.Infrastructure.Delivery.Http.TelegramController import TelegramController

def main():
    load_dotenv()
    print("Environment variables loaded for ri-telegram-bot.")

    client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    db = client[settings.MONGO_DB_NAME]
    user_repo = MongoUserRepository(db)

    # register_use_case = RegisterUserActivity(user_repository=user_repo)
    # spam_check_case = ProcessSpamCheck(user_repository = user_repo)
    handle_message_use_case = HandleUserMessage(user_repository = user_repo)
    
    controller = TelegramController(
        handle_message_use_case = handle_message_use_case
    )

    token = settings.TELEGRAM_TOKEN
    app = ApplicationBuilder().token(token = token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), controller.handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
