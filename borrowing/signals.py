from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from borrowing.models import Borrowing


def cache_invalidate_by_prefix(prefix: str) -> int:
    return cache.delete_pattern(f"*.{prefix}.*")


@receiver(post_save, sender=Borrowing)
def borrowing_save_invalidate_cache(sender, **kwargs):
    cache_invalidate_by_prefix("borrowings")
