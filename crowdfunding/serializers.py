from rest_framework import serializers
from django.utils import timezone
from .models import Collect, Payment
from django.contrib.auth.models import User
from .validators import validate_future_date, validate_payment_amount, validate_collect_active


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PaymentSerializer(serializers.ModelSerializer):
    donator = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'donator', 'amount', 'comment', 'date_added']
        read_only_fields = ['date_added']


class CollectSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()
    donors_count = serializers.ReadOnlyField()

    class Meta:
        model = Collect
        fields = [
            'id', 'author', 'name', 'occasion', 'description',
            'target_amount', 'current_amount', 'end_datetime',
            'created_at', 'updated_at', 'is_active', 'donors_count', 'payments'
        ]
        read_only_fields = ['current_amount', 'created_at', 'updated_at']


class CollectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = ['name', 'occasion', 'description', 'target_amount', 'end_datetime']

    def validate_end_datetime(self, value):
        """Валидация даты завершения"""
        if value <= timezone.now():
            raise serializers.ValidationError("Дата завершения должна быть в будущем")
        return value

    def validate_target_amount(self, value):
        """Валидация целевой суммы"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Целевая сумма должна быть положительной")
        return value


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['collect', 'amount', 'comment']

    def validate_amount(self, value):
        """Валидация суммы платежа"""
        if value <= 0:
            raise serializers.ValidationError("Сумма платежа должна быть положительной")
        return value

    def validate(self, data):
        """Дополнительная валидация платежа"""
        collect = data.get('collect')
        amount = data.get('amount')

        if collect and amount:
            # Проверяем что сбор активен
            if not collect.is_active:
                raise serializers.ValidationError({"collect": "Нельзя внести платеж в завершенный сбор"})

            # Проверяем что не превышаем целевую сумму
            if collect.target_amount and collect.current_amount + amount > collect.target_amount:
                remaining = collect.target_amount - collect.current_amount
                raise serializers.ValidationError({
                    "amount": f"Платеж превышает целевую сумму. Осталось собрать: {remaining}"
                })

        return data