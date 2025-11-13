from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from crowdfunding.models import Collect, Payment


class Command(BaseCommand):
    help = 'Наполняет базу данных тестовыми данными для краудфандинга'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Количество тестовых пользователей'
        )
        parser.add_argument(
            '--collects',
            type=int,
            default=20,
            help='Количество тестовых сборов'
        )
        parser.add_argument(
            '--payments',
            type=int,
            default=50,
            help='Количество тестовых платежей'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        collects_count = options['collects']
        payments_count = options['payments']

        self.stdout.write('🎯 Начинаем наполнение базы тестовыми данными...')

        # 1. Создаем пользователей
        self.stdout.write('👥 Создаем пользователей...')
        users = []
        for i in range(users_count):
            username = f'user{i + 1}'
            email = f'user{i + 1}@example.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'   Создан пользователь: {username}')
            users.append(user)

        # 2. Создаем сборы
        self.stdout.write('💰 Создаем сборы...')
        occasions = [
            ('birthday', 'День рождения'),
            ('wedding', 'Свадьба'),
            ('medical', 'Медицинское лечение'),
            ('charity', 'Благотворительность'),
            ('other', 'Другое')
        ]

        collect_names = [
            "Помощь в лечении",
            "Сбор на операцию",
            "На день рождения",
            "На свадебное путешествие",
            "Благотворительный сбор",
            "Помощь семье",
            "Образовательный проект",
            "Творческий проект",
            "Спортивный сбор",
            "Экологический проект"
        ]

        collects = []
        for i in range(collects_count):
            occasion = random.choice(occasions)
            collect = Collect.objects.create(
                author=random.choice(users),
                name=f"{random.choice(collect_names)} #{i + 1}",
                occasion=occasion[0],
                description=f"Это тестовое описание для сбора '{random.choice(collect_names)}'. " +
                            f"Мы собираем средства на важное дело и будем благодарны за любую помощь!",
                target_amount=random.choice([None, 50000, 100000, 200000, 500000]),
                end_datetime=timezone.now() + timedelta(days=random.randint(30, 365))
            )
            collects.append(collect)
            self.stdout.write(f'   Создан сбор: {collect.name}')

        # 3. Создаем платежи
        self.stdout.write('💳 Создаем платежи...')
        payment_comments = [
            "Желаю успехов в сборе!",
            "Надеюсь, это поможет",
            "От всей души",
            "Пусть все получится",
            "Будьте здоровы",
            "Удачи в вашем деле",
            "Спасибо за вашу работу",
            "Надеюсь на лучшее",
            "Верю в ваш успех",
            "От чистого сердца"
        ]

        for i in range(payments_count):
            collect = random.choice(collects)
            donator = random.choice(users)

            # Проверяем что донатор не автор сбора
            while donator == collect.author:
                donator = random.choice(users)

            payment = Payment.objects.create(
                donator=donator,
                collect=collect,
                amount=random.randint(100, 10000),
                comment=random.choice(payment_comments)
            )

            # Обновляем сумму сбора через сигналы
            collect.refresh_from_db()

            if (i + 1) % 10 == 0:
                self.stdout.write(f'   Создано платежей: {i + 1}')

        # 4. Выводим статистику
        self.stdout.write('\n📊 Статистика базы данных:')
        self.stdout.write(f'   👥 Пользователей: {User.objects.count()}')
        self.stdout.write(f'   💰 Сборов: {Collect.objects.count()}')
        self.stdout.write(f'   💳 Платежей: {Payment.objects.count()}')

        total_amount = sum(collect.current_amount for collect in Collect.objects.all())
        active_collects = Collect.objects.filter(end_datetime__gt=timezone.now()).count()

        self.stdout.write(f'   💵 Общая собранная сумма: {total_amount} руб.')
        self.stdout.write(f'   🟢 Активных сборов: {active_collects}')

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ База данных успешно наполнена тестовыми данными!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '🌐 Проверьте данные в админке: http://127.0.0.1:8000/admin/'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '🔗 Или через API: http://127.0.0.1:8000/api/collects/'
            )
        )