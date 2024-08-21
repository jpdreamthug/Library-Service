from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from borrowing.models import Borrowing
from notification.telegram_bot import TelegramBot


@shared_task
def send_notification_overdue_tasks():
    queryset = Borrowing.objects.filter(
        expected_return_date__lte=timezone.now().date() + timedelta(days=1),
        actual_return_date__isnull=True,
    )

    bot = TelegramBot(token=settings.TELEGRAM_BOT_TOKEN)
    chat_id = settings.TELEGRAM_CHAT_ID
    if not queryset.exists():
        bot.send_message_to_chat(
            message="No overdue borrowings",
            chat_id=chat_id,
        )
    for borrowing in queryset:
        message = ""
        if (borrowing.expected_return_date
                == timezone.now().date() + timedelta(days=1)):
            message = (
                f"Tomorrow borrowing book will be overdue\n"
                f"Book: {borrowing.book}\n"
                f"User: {borrowing.user}\n"
            )
        else:
            message = (
                f"Borrowing book overdue found\n"
                f"Book: {borrowing.book}\n"
                f"User: {borrowing.user.email}\n"
                f"Expected date {borrowing.expected_return_date}\n"
            )

        bot.send_message_to_chat(
            message=message,
            chat_id=chat_id,
        )
