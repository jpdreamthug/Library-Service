from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing.models import Borrowing
from django.conf import settings
from notification.telegram_bot import TelegramBot


@receiver(post_save, sender=Borrowing)
def borrowing_post_save_signal_handler(sender, **kwargs):
    bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
    user = kwargs["instance"].user
    bot.send_message_to_chat(
        chat_id=settings.TELEGRAM_CHAT_ID,
        message=f"Borrowing successful registered by {user.email}",
    )
