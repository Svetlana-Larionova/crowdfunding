from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

def validate_future_date(value):
    """Проверяет что дата в будущем"""
    if value <= timezone.now():
        raise ValidationError('Дата завершения должна быть в будущем')

def validate_positive_amount(value):
    """Проверяет что сумма положительная"""
    if value <= Decimal('0'):
        raise ValidationError('Сумма должна быть положительной')

def validate_target_amount(value):
    """Проверяет целевую сумму"""
    if value is not None and value <= Decimal('0'):
        raise ValidationError('Целевая сумма должна быть положительной или пустой')

def validate_payment_amount(collect, amount):
    """Проверяет платеж на превышение целевой суммы"""
    if collect.target_amount and collect.current_amount + amount > collect.target_amount:
        raise ValidationError(
            f'Платеж превышает целевую сумму. Осталось собрать: {collect.target_amount - collect.current_amount}'
        )

def validate_collect_active(collect):
    """Проверяет что сбор активен"""
    if not collect.is_active:
        raise ValidationError('Нельзя внести платеж в завершенный сбор')