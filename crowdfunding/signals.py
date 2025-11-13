from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.cache import cache
from .models import Collect, Payment
from .tasks import send_collect_created_email, send_payment_created_email, send_collect_goal_reached_email


def clear_collect_cache():
    """Очищает кэш для всех сборов"""
    cache.clear()


@receiver(post_save, sender=Collect)
def on_collect_save(sender, instance, created, **kwargs):
    """Обработчик сохранения сбора"""
    if created:
        # Отправляем email о создании сбора
        send_collect_created_email.delay(instance.id)

    clear_collect_cache()


@receiver(post_save, sender=Payment)
def on_payment_save(sender, instance, created, **kwargs):
    """Обработчик сохранения платежа"""
    if created:
        with transaction.atomic():
            # Обновляем сумму сбора
            collect = instance.collect
            collect.current_amount += instance.amount
            collect.save()

            # Отправляем emails о платеже
            send_payment_created_email.delay(instance.id)

            # Проверяем достижение цели
            if collect.target_amount and collect.current_amount >= collect.target_amount:
                send_collect_goal_reached_email.delay(collect.id)

    clear_collect_cache()


@receiver(post_delete, sender=Payment)
def on_payment_delete(sender, instance, **kwargs):
    """Обработчик удаления платежа"""
    with transaction.atomic():
        collect = instance.collect
        collect.current_amount -= instance.amount
        collect.save()
        clear_collect_cache()


@receiver(post_delete, sender=Collect)
def on_collect_delete(sender, instance, **kwargs):
    """Обработчик удаления сбора"""
    clear_collect_cache()