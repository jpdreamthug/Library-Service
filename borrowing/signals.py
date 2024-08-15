from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from borrowing.models import Borrowing
from book.signals import cache_invalidate_by_prefix
from notification.telegram_bot import TelegramBot
from payment.models import Payment

payment_successful = Signal()


@receiver(post_save, sender=Borrowing)
def borrowing_save_invalidate_cache(sender, **kwargs):
    cache_invalidate_by_prefix("borrowings")


@receiver(payment_successful, sender=Payment)
def payment_successful_handler(sender, instance, **kwargs):
    bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
    bot.send_message_to_chat(
        chat_id=settings.TELEGRAM_CHAT_ID,
        message=f"Payment for borrowing successful\n"
        f"Book: {instance.borrowing.book}\n"
        f"Price: {instance.money_to_pay / 100}$\n"
        f"Payment type: {instance.type}\n"
        f"User: {instance.borrowing.user.email}",
    )
