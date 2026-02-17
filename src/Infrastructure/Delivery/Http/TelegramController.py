from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

# Use Cases
from src.Application.UseCase.RegisterUserActivity import RegisterUserActivity
from src.Application.UseCase.ProcessSpamCheck import ProcessSpamCheck
from src.Application.UseCase.HandleUserMessage import HandleUserMessage
from src.Application.UseCase.UnmuteUser import UnmuteUser

# Infra
from src.Infrastructure.Config.Settings import settings

class TelegramController:

    def __init__(
            self, 
            handle_message_use_case: HandleUserMessage,
            handle_unmute_use_case: UnmuteUser
        ):
        self.handle_message_case = handle_message_use_case
        self.handle_unmute_use_case = handle_unmute_use_case
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if user_id != settings.OWNER_ID:
            return
        
        await update.message.reply_text("🏓 Pong! Bot is alive and kicking.")
    
    async def handle_unmute(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in ['administrator', 'creator']:
            return
        
        target_user = None
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        
        if not target_user:
            return
        
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_photos = True,
                can_send_videos = True
            )
        )

        self.handle_unmute_use_case.execute(target_user.id)

        await update.message.reply_text(
            f"✅ El usuario {target_user.mention_markdown_v2()} ha sido desbloqueado y ya puede escribir\\.",
            parse_mode="MarkdownV2"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user = update.effective_user
        chat = update.effective_chat

        if not tg_user or tg_user.is_bot or chat.type == "private":
            return
        
        result = self.handle_message_case.execute(
            user_id = tg_user.id,
            username = tg_user.username,
            first_name = tg_user.first_name
        )

        if result == "warn":
            await update.message.reply_text(f"⚠️ {tg_user.first_name}, don't spam!")

        elif result == "mute":
            try:
                await update.message.delete()
                
                # Restrict the user
                await context.bot.restrict_chat_member(
                    chat_id = chat.id,
                    user_id = tg_user.id,
                    permissions = ChatPermissions(
                        can_send_messages = False,
                        can_send_photos = False,
                        can_send_videos = False
                    )
                )

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🔇 User {tg_user.first_name} has been restricted for spamming."
                )

            except Exception as e:
                print(f"Execption TelegramController: {e}")
