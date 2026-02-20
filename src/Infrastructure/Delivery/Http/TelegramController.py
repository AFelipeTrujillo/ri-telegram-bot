from telegram import Update, ChatPermissions
from telegram.constants import ChatType
from telegram.ext import ContextTypes

# Use Cases
from src.Application.DTO.UserActivityDTO import UserActivityDTO
from src.Application.UseCase.HandleUserMessage import HandleUserMessage
from src.Application.UseCase.UnmuteUser import UnmuteUser
from src.Application.UseCase.HandlePing import HandlePing
from src.Application.UseCase.FilterLink import FilterLink
from src.Application.UseCase.FilterInlineButtons import FilterInlineButtons
from src.Application.UseCase.WhitelistUser import WhitelistUser

# Infra
from src.Infrastructure.Config.Settings import settings

class TelegramController:

    def __init__(
            self, 
            handle_message: HandleUserMessage,
            handle_unmute: UnmuteUser,
            handle_ping: HandlePing,
            handle_filter_link: FilterLink,
            handle_filter_inline_buttons: FilterInlineButtons,
            handle_whitelist_user: WhitelistUser

        ):
        self.handle_message_case = handle_message
        self.handle_unmute_use_case = handle_unmute
        self.handle_ping_use_case = handle_ping
        self.handle_filter_link_use_case = handle_filter_link
        self.handle_filter_inline_buttons = handle_filter_inline_buttons
        self.handle_whitelist_user = handle_whitelist_user
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if self.handle_ping_use_case.execute(user_id):
            await update.message.reply_text("Pong! Bot is alive and kicking.")
    
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

        # TODO: Create the silence mode
        # await update.message.reply_text(
        #    f"✅ El usuario {target_user.mention_markdown_v2()} ha sido desbloqueado y ya puede escribir\\.",
        #    parse_mode="MarkdownV2"
        #)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        dto = self._extract_dto(update)
        is_admin = await self._check_if_admin(update)

        link_decision = self.handle_filter_link_use_case.execute(dto, is_admin)
        if link_decision != "allow":
            return await self._apply_link_sanction(link_decision, update, context)

        inline_decision = self.handle_filter_inline_buttons.execute(dto, is_admin)
        if inline_decision != "allow":
            return await self._apply_inline_buttons(inline_decision, update, context)


        spam_decision = self.handle_message_case.execute(dto)
        if spam_decision != "allow":
            return await self._apply_spam_sanction(spam_decision, update, context)


    async def handle_whitelist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        chat_type = update.effective_chat.type

        if user_id != settings.OWNER_ID and chat_type != ChatType.PRIVATE:
            await update.effective_message.delete()
            return

        if not context.args:
            await update.message.reply_text("Please indicate the ID: /whitelist 12345678")

        try:
            target_id = int(context.args[0])
            success = self.handle_whitelist_user.execute(target_user_id = target_id)
            if success:
                await update.message.reply_text(f"The user {target_id} has been added to the whitelist")
            else:
                await update.message.reply_text(f"The user {target_id} does not exist in the database")
        except ValueError:
            await update.message.reply_text("The ID has to be INT")
    
    async def _handle_link_filtering(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:

        tg_user = update.effective_user
        chat = update.effective_chat

        has_links = any(e.type in ['url', 'text_link'] for e in update.message.entities) if update.message.entities else False
        if not has_links:
            return False

        member = await chat.get_member(tg_user.id)
        is_admin = member.status in ['administrator', 'creator']

        decision = self.handle_filter_link_use_case.execute(
            user_id=tg_user.id,
            first_name=tg_user.first_name,
            has_entities=True,
            is_admin=is_admin
        )

        if "delete" in decision:
            content = update.message.text or "[Media/Other]"
            await update.message.delete()
            await self._send_owner_report(tg_user, chat, content, context)
            
            if decision == "mute_and_delete":
                await self._mute_user(chat.id, tg_user, context, reason="Link violation limit")
            
            return True

        return False
    
    async def _send_owner_report(self, user, chat, content, context):

        username = f"@{user.username}" if user.username else "No username"
        
        report = (
            "🛡 LINK DELETED\n"
            f"User ID: {user.id}\n"
            f"User: {user.first_name} ({username})\n"
            f"Group: {chat.title}\n"
            f"Content: {content}"
        )
        
        try:
            await context.bot.send_message(
                chat_id=settings.OWNER_ID, 
                text=report
            )
        except Exception as e:
            print(f"Error sending plain text report: {e}")

    async def _mute_user(self, chat_id: int, user, context: ContextTypes.DEFAULT_TYPE, reason: str):
        
        try:
            
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_photos=False,
                    can_send_videos=False,
                    can_add_web_page_previews=False
                )
            )

        except Exception as e:
            
            await context.bot.send_message(
                chat_id=settings.OWNER_ID,
                text=f"❌ Failed to mute user {user.id} in {chat_id}. Check bot permissions!"
            )

    def _extract_dto(self, update: Update) -> UserActivityDTO:
        user = update.effective_user
        message = update.effective_message

        has_links = any(e.type in ['url', 'text_link'] for e in message.entities) if message.entities else False

        has_inline_buttons = False
        if message.reply_markup and message.reply_markup.inline_keyboard:
            has_inline_buttons = len(message.reply_markup.inline_keyboard) > 0

        return UserActivityDTO(
            user_id     = user.id,
            first_name  = user.first_name,
            username    = user.username,
            language_code = user.language_code,
            is_premium  = getattr(user, 'is_premium', False),
            has_links   = has_links,
            has_inline_buttons = has_inline_buttons,
            content     = message.text,
            source      = "organic"
        )
    
    async def _check_if_admin(self, update: Update) -> bool:
        if update.effective_user.id == settings.OWNER_ID:
            return True
        
        member = await update.effective_chat.get_member(update.effective_user.id)
        return member.status in ['administrator', 'creator']

    async def _apply_link_sanction(self, decision: str, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if decision == "delete" or decision == "mute_and_delete":
            await update.message.delete()

        if decision == "mute_and_delete":
            await self._mute_user(
                update.effective_chat.id,
                update.effective_user,
                context,
                reason="Link violation limit"
            )
        
        await self._send_owner_report(update.effective_user, update.effective_chat, update.message.text, context)

    async def _apply_spam_sanction(self, decision: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if decision == "warning":
            await update.message.delete()
            await update.message.reply_text(f"⚠️ {update.effective_user.first_name}, slow down! Don't spam.")
        elif decision == "mute":
            # TODO: Create the silicen mode from .env
            # await update.message.reply_text(f"🔇 {update.effective_user.first_name} has been muted for flooding the chat.")
            await update.message.delete()
            await self._mute_user(
                update.effective_chat.id,
                update.effective_user, 
                context, 
                reason="Spamming"
            )

    async def _apply_inline_buttons(self, decision: str, update: Update, context: ContextTypes.DEFAULT_TYPE):

        if decision == "delete":
            try:
                await update.message.delete()
            except Exception as e:
                print(f"TelegramControler._apply_inline_buttons: {e}")