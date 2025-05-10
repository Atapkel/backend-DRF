from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection
from .models import Event  # Ensure this imports your Event model correctly

@receiver(post_save, sender=Event)
def invalidate_cache_on_save(sender, instance, **kwargs):
    print(f"Event saved (ID: {instance.id}), invalidating cache...")
    conn = get_redis_connection("default")
    conn.delete_pattern("event_list:*")  # Changed from product_list to event_list

@receiver(post_delete, sender=Event)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    print(f"Event deleted (ID: {instance.id}), invalidating cache...")
    conn = get_redis_connection("default")
    conn.delete_pattern("event_list:*")  # Changed from product_list to event_list