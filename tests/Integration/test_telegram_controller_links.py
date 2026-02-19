import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import MessageEntity

@pytest.mark.asyncio
class TestTelegramControllerLinks:

    @pytest.fixture
    def controller(self):
        
        from src.Infrastructure.Delivery.Http.TelegramController import TelegramController
        return TelegramController(
            handle_message_use_case=AsyncMock(),
            handle_ping_use_case=AsyncMock(),
            handle_unmute_use_case=AsyncMock(),
            handle_filter_link_use_case=MagicMock(),
            handle_filter_inline_buttons=MagicMock()
        )

    async def test_handle_link_filtering_should_delete_when_violation(self, controller):
 
        update = MagicMock()
        context = MagicMock()
        context.bot.send_message = AsyncMock()
        
        update.message.text = "Check this link: http://spam.com"
        entity = MagicMock(spec=MessageEntity)
        entity.type = 'url'
        update.message.entities = [entity]
        update.message.delete = AsyncMock()
        
        update.effective_chat.get_member = AsyncMock()
        member = MagicMock()
        member.status = 'member'
        update.effective_chat.get_member.return_value = member

        controller.handle_filter_link_use_case.execute.return_value = "delete"

        result = await controller._handle_link_filtering(update, context)

        assert result is True  
        update.message.delete.assert_called_once()  
        context.bot.send_message.assert_called_once()  