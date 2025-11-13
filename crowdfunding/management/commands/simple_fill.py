from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from crowdfunding.models import Collect, Payment


class Command(BaseCommand):
    help = 'Простая команда для наполнения базы без писем'

    def handle(self, *args, **options):
        print("🎯 Создаем тестовые данные (без писем)...")

        # Временно отключаем сигналы
        from django.db.models import signals
        from crowdfunding import signals as crowdfunding_signals

        # Отключаем сигналы чтобы не отправлять письма
        signals.post_save.disconnect(crowdfunding_signals.on_collect_save, sender=Collect)
        signals.post_save.disconnect(crowdfunding_signals.on_payment_save, sender=Payment)

        try:
            # Создаем пользователей
            user1 = User.objects.create_user('testuser1', 'test1@example.com', 'pass123')
            user2 = User.objects.create_user('testuser2', 'test2@example.com', 'pass123')

            print("👥 Пользователи созданы")

            # Создаем сборы
            collect1 = Collect.objects.create(
                author=user1,
                name="Тестовый сбор 1",
                occasion="birthday",
                description="Тестовое описание 1",
                target_amount=50000,
                end_datetime=timezone.now() + timedelta(days=30)
            )

            collect2 = Collect.objects.create(
                author=user2,
                name="Тестовый сбор 2",
                occasion="medical",
                description="Тестовое описание 2",
                target_amount=100000,
                end_datetime=timezone.now() + timedelta(days=60)
            )

            print("💰 Сборы созданы")

            # Создаем платежи вручную (без сигналов)
            Payment.objects.create(donator=user2, collect=collect1, amount=1000)
            Payment.objects.create(donator=user1, collect=collect2, amount=2000)

            # Обновляем суммы вручную
            collect1.current_amount = 1000
            collect1.save()
            collect2.current_amount = 2000
            collect2.save()

            print("💳 Платежи созданы")
            print("✅ Готово! Данные созданы без писем.")

        finally:
            # Включаем сигналы обратно
            signals.post_save.connect(crowdfunding_signals.on_collect_save, sender=Collect)
            signals.post_save.connect(crowdfunding_signals.on_payment_save, sender=Payment)