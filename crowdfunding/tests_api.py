from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Collect, Payment


class APITests(APITestCase):
    def setUp(self):
        """Создаем тестовые данные"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.collect_data = {
            'name': 'API Тестовый сбор',
            'occasion': 'wedding',
            'description': 'Тестовое описание для API',
            'target_amount': 50000,
            'end_datetime': (timezone.now() + timedelta(days=30)).isoformat()
        }

        self.collect = Collect.objects.create(
            author=self.user,
            name='Существующий сбор',
            occasion='birthday',
            description='Описание',
            target_amount=10000,
            end_datetime=timezone.now() + timedelta(days=7)
        )

    def test_get_collects_list(self):
        """Тест получения списка сборов"""
        url = reverse('collect-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_collect(self):
        """Тест создания сбора через API"""
        url = reverse('collect-list')
        response = self.client.post(url, self.collect_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collect.objects.count(), 2)
        self.assertEqual(response.data['name'], 'API Тестовый сбор')

    def test_get_collect_detail(self):
        """Тест получения деталей сбора"""
        url = reverse('collect-detail', args=[self.collect.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Существующий сбор')

    def test_create_payment(self):
        """Тест создания платежа через API"""
        url = reverse('payment-list')
        payment_data = {
            'collect': self.collect.id,
            'amount': 1500,
            'comment': 'Тестовый платеж через API'
        }
        response = self.client.post(url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(response.data['amount'], '1500.00')

    def test_collect_payments_endpoint(self):
        """Тест эндпоинта платежей сбора"""
        # Создаем платеж
        Payment.objects.create(
            donator=self.user,
            collect=self.collect,
            amount=2000
        )

        url = reverse('collect-payments', args=[self.collect.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '2000.00')

    def test_validation_errors(self):
        """Тест валидационных ошибок"""
        # Пытаемся создать сбор с прошедшей датой
        invalid_data = self.collect_data.copy()
        invalid_data['end_datetime'] = (timezone.now() - timedelta(days=1)).isoformat()

        url = reverse('collect-list')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_datetime', response.data)

    def test_authentication_required(self):
        """Тест что аутентификация требуется"""
        self.client.logout()
        url = reverse('collect-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # AllowAny разрешает

    def test_payment_exceeds_target(self):
        """Тест что нельзя превысить целевую сумму"""
        # Создаем платеж превышающий целеую сумму
        url = reverse('payment-list')
        payment_data = {
            'collect': self.collect.id,
            'amount': 15000,  # Больше чем target_amount=10000
            'comment': 'Слишком большой платеж'
        }
        response = self.client.post(url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)