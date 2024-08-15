from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing.models import Borrowing
from book.signals import cache_invalidate_by_prefix


@receiver(post_save, sender=Borrowing)
def borrowing_save_invalidate_cache(sender, **kwargs):
    cache_invalidate_by_prefix("borrowings")
