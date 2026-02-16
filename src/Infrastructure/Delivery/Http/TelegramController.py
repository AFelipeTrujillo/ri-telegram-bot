from telegram import Update
from telegram.ext import ContextTypes

from src.Application.UseCase.RegisterUserActivity import RegisterUserActivity
from src.Application.UseCase.ProcessSpamCheck import ProcessSpamCheck
from src.Application.UseCase.HandleUserMessage import HandleUserMessage

class TelegramController:

    def __init__(
            self, 
            handle_message_use_case: HandleUserMessage,
        ):
        self.use_case = handle_message_use_case
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user = update.effective_user
        if not tg_user:
            return
        
        result = self.use_case.execute(
            user_id = tg_user.id,
            username = tg_user.username,
            first_name = tg_user.first_name
        )

        if result == "warn":
            await update.message.reply_text(f"⚠️ {tg_user.first_name}, don't spam!")

        elif result == "mute":
            await update.message.delete()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🔇 User {tg_user.first_name} has been restricted for spamming."
            )
