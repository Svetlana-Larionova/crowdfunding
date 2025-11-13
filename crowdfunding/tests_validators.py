from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Collect, Payment
from .validators import validate_future_date, validate_payment_amount, validate_collect_active


class ValidatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.collect = Collect.objects.create(
            author=self.user,
            name='Тестовый сбор',
            occasion='birthday',
            description='Тестовое описание',
            target_amount=10000,
            end_datetime=timezone.now() + timedelta(days=7)
        )

    def test_validate_future_date_success(self):
        """Тест успешной валидации будущей даты"""
        future_date = timezone.now() + timedelta(days=1)
        try:
            validate_future_date(future_date)
        except ValidationError:
            self.fail("validate_future_date вызвал ValidationError для будущей даты")

    def test_validate_future_date_failure(self):
        """Тест валидации прошедшей даты"""
        past_date = timezone.now() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_future_date(past_date)

    def test_validate_payment_amount_success(self):
        """Тест успешной валидации суммы платежа"""
        try:
            validate_payment_amount(self.collect, 5000)
        except ValidationError:
            self.fail("validate_payment_amount вызвал ValidationError для допустимой суммы")

    def test_validate_payment_amount_exceeds(self):
        """Тест валидации превышения целевой суммы"""
        with self.assertRaises(ValidationError):
            validate_payment_amount(self.collect, 15000)

    def test_validate_collect_active_success(self):
        """Тест успешной валидации активного сбора"""
        try:
            validate_collect_active(self.collect)
        except ValidationError:
            self.fail("validate_collect_active вызвал ValidationError для активного сбора")

    def test_validate_collect_active_failure(self):
        """Тест валидации завершенного сбора"""
        # Создаем завершенный сбор
        expired_collect = Collect.objects.create(
            author=self.user,
            name='Завершенный сбор',
            occasion='charity',
            description='Завершен',
            end_datetime=timezone.now() - timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            validate_collect_active(expired_collect)