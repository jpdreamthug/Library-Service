from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from book.models import Book


def cache_invalidate_by_prefix(prefix: str) -> int:
    return cache.delete_pattern(f"*.{prefix}.*")


@receiver(post_save, sender=Book)
def book_save_invalidate_cache(sender, **kwargs):
    cache_invalidate_by_prefix("books_list")
