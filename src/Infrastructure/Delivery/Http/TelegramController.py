from telegram import Update
from telegram.ext import ContextTypes

from src.Application.UseCase.RegisterUserActivity import RegisterUserActivity

class TelegramController:

    def __init__(self, register_user_case: RegisterUserActivity):
        self.use_case = register_user_case
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user = update.effective_user
        if not tg_user:
            return
        
        self.use_case.execute(
            user_id = tg_user.id,
            username = tg_user.username,
            first_name = tg_user.first_name
        )