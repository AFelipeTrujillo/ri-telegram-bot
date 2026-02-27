import os
from os import stat_result

import certifi

from dotenv import load_dotenv

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from telegram.ext import CommandHandler

from src.Application.UseCase.FilterBotUnauthorized import FilterBotUnauthorized
from src.Application.UseCase.HandleUserCommand import HandleUserCommand
#Use Cases
from src.Application.UseCase.HandleUserMessage import HandleUserMessage
from src.Application.UseCase.UnmuteUser import UnmuteUser
from src.Application.UseCase.HandlePing import HandlePing
from src.Application.UseCase.FilterLink import FilterLink
from src.Application.UseCase.FilterInlineButtons import FilterInlineButtons
from src.Application.UseCase.WhitelistUser import WhitelistUser

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
    handle_unmute_use_case = UnmuteUser(user_repository=user_repo)
    handle_ping_use_case = HandlePing()
    handle_filter_link_use_case = FilterLink(user_repository = user_repo)
    handle_filter_inline_buttons_use_case = FilterInlineButtons(user_repository = user_repo)
    handle_whitelist_user = WhitelistUser(user_repository=user_repo)

    telegram_controller = TelegramController(
        handle_message= handle_message_use_case,
        handle_unmute= handle_unmute_use_case,
        handle_ping= handle_ping_use_case,
        handle_filter_link= handle_filter_link_use_case,
        handle_filter_inline_buttons = handle_filter_inline_buttons_use_case,
        handle_whitelist_user = handle_whitelist_user,
        handle_bot_unauthorized= FilterBotUnauthorized(user_repository=user_repo),
        handle_user_command= HandleUserCommand(user_repository=user_repo)
    )

    token = settings.TELEGRAM_TOKEN
    app = ApplicationBuilder().token(token = token).build()

    app.add_handler(CommandHandler("ping", telegram_controller.handle_ping))
    app.add_handler(CommandHandler("unmute", telegram_controller.handle_unmute))
    app.add_handler(CommandHandler("whitelist", telegram_controller.handle_whitelist_command))
    # app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), telegram_controller.handle_message))
    app.add_handler(
        MessageHandler( 
            (filters.TEXT | filters.COMMAND | filters.Sticker.ALL | filters.CAPTION | filters.ANIMATION), 
            telegram_controller.handle_message
        )
    )

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
