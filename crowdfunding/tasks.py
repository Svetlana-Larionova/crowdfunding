from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Collect, Payment


@shared_task
def send_collect_created_email(collect_id):
    """Отправляет email автору при создании сбора"""
    try:
        collect = Collect.objects.get(id=collect_id)

        subject = f'🎉 Сбор "{collect.name}" успешно создан!'
        message = f'''
        Здравствуйте, {collect.author.username}!

        Ваш сбор "{collect.name}" успешно создан и теперь доступен для пожертвований.

        Детали сбора:
        - Название: {collect.name}
        - Повод: {collect.get_occasion_display()}
        - Целевая сумма: {collect.target_amount or "Не ограничена"}
        - Дата завершения: {collect.end_datetime.strftime("%d.%m.%Y")}

        Ссылка на сбор: http://127.0.0.1:8000/api/collects/{collect.id}/

        Спасибо, что используете нашу платформу!
        Команда Crowdfunding
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[collect.author.email],
            fail_silently=False,
        )

        return f'Email отправлен автору сбора {collect.name}'
    except Collect.DoesNotExist:
        return 'Сбор не найден'


@shared_task
def send_payment_created_email(payment_id):
    """Отправляет email донатору и автору сбора при создании платежа"""
    try:
        payment = Payment.objects.select_related('collect', 'donator', 'collect__author').get(id=payment_id)
        collect = payment.collect

        # Email донатору
        donor_subject = f'💝 Спасибо за ваше пожертвование!'
        donor_message = f'''
        Здравствуйте, {payment.donator.username}!

        Благодарим вас за пожертвование в размере {payment.amount} руб. 
        в сбор "{collect.name}".

        Ваш комментарий: "{payment.comment or 'Без комментария'}"
        Дата пожертвования: {payment.date_added.strftime("%d.%m.%Y %H:%M")}

        Сумма сбора теперь составляет: {collect.current_amount} руб.
        {f"Осталось собрать: {collect.target_amount - collect.current_amount} руб." if collect.target_amount else ""}

        Спасибо за вашу поддержку!
        Команда Crowdfunding
        '''

        send_mail(
            subject=donor_subject,
            message=donor_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.donator.email],
            fail_silently=False,
        )

        # Email автору сбора (если донатор не автор)
        if payment.donator != collect.author:
            author_subject = f'🎊 Новое пожертвование в вашем сборе!'
            author_message = f'''
            Здравствуйте, {collect.author.username}!

            В ваш сбор "{collect.name}" поступило новое пожертвование!

            Детали пожертвования:
            - Донатор: {payment.donator.username}
            - Сумма: {payment.amount} руб.
            - Комментарий: "{payment.comment or 'Без комментария'}"
            - Дата: {payment.date_added.strftime("%d.%m.%Y %H:%M")}

            Текущая сумма сбора: {collect.current_amount} руб.
            {f"Прогресс: {(collect.current_amount / collect.target_amount * 100):.1f}%" if collect.target_amount else ""}

            Продолжайте в том же духе!
            Команда Crowdfunding
            '''

            send_mail(
                subject=author_subject,
                message=author_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[collect.author.email],
                fail_silently=False,
            )

        return f'Emails отправлены для платежа {payment.id}'
    except Payment.DoesNotExist:
        return 'Платеж не найден'


@shared_task
def send_collect_goal_reached_email(collect_id):
    """Отправляет email при достижении целевой суммы"""
    try:
        collect = Collect.objects.get(id=collect_id)

        if collect.target_amount and collect.current_amount >= collect.target_amount:
            subject = f'🎯 Поздравляем! Целевая сумма достигнута!'
            message = f'''
            Здравствуйте, {collect.author.username}!

            Отличные новости! Ваш сбор "{collect.name}" 
            достиг целевой суммы {collect.target_amount} руб.!

            Текущая сумма: {collect.current_amount} руб.
            Количество донаторов: {collect.donors_count}

            Сбор продолжит принимать пожертвования до {collect.end_datetime.strftime("%d.%m.%Y")}.

            Поздравляем с успешным сбором!
            Команда Crowdfunding
            '''

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[collect.author.email],
                fail_silently=False,
            )

            return f'Email о достижении цели отправлен для сбора {collect.name}'
    except Collect.DoesNotExist:
        return 'Сбор не найден'