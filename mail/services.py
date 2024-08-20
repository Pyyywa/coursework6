import random
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.core.cache import cache

from mail.models import Logs, MailSettings, Client
from blog.models import Article
import logging

logger = logging.getLogger(__name__)


def send_email(mail_settings):
    """ Отправка рассылки """

    clients = mail_settings.client.all()
    clients_list = [client.email for client in clients]

    server_response = None
    status = Logs.STATUS_FAILED

    try:
        result = send_mail(
            subject=mail_settings.message.title,
            message=mail_settings.message.message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=clients_list,
        )

        if result:
            status = Logs.STATUS_SUCCESS
            server_response = "OK"

    except SMTPException as e:
        server_response = str(e)

    Logs.objects.create(
        status=status,
        mail=mail_settings,
        answer_server=server_response
    )


def my_job():
    """ Проверяет необходима ли рассылка почты """

    now = timezone.now()
    for mail_settings in MailSettings.objects.filter(
            status=MailSettings.STATUS_IN_PROCESS):
        if (now.timestamp() > mail_settings.start_time.timestamp()) and (
                now.timestamp() < mail_settings.end_time.timestamp()):
            mail_log = Logs.objects.filter(mail=mail_settings)
            if mail_log.exists():

                last_try_date = mail_log.order_by('-last_try').first().last_try
                mail_period = mail_settings.period
                if mail_period == MailSettings.PERIOD_DAILY:
                    if (now - last_try_date).days >= 1:
                        send_email(mail_settings)
                elif mail_period == MailSettings.PERIOD_WEEKLY:
                    if (now - last_try_date).days >= 7:
                        send_email(mail_settings)
                elif mail_period == MailSettings.PERIOD_MONTHLY:
                    if (now - last_try_date).days >= 30:
                        send_email(mail_settings)
            else:
                send_email(mail_settings)


def get_cached_data():
    """ Кэширование для главной страницы (всего рассылок, активные рассылки,
    уникальные клиенты"""

    if settings.CACHE_ENABLED:
        total_mail_counter = cache.get('total_mail_counter')
        active_mail_counter = cache.get('active_mail_counter')
        unique_client_counter = cache.get('unique_client_counter')

        if total_mail_counter is None:
            total_mail_counter = MailSettings.objects.all()
            cache.get('total_mail_counter', total_mail_counter)
        else:
            total_mail_counter = MailSettings.objects.all()

        if active_mail_counter is None:
            active_mail_counter = MailSettings.objects.filter(
                status=MailSettings.STATUS_IN_PROCESS)
            cache.get('active_mail_counter', active_mail_counter)
        else:
            active_mail_counter = MailSettings.objects.filter(
                status=MailSettings.STATUS_IN_PROCESS)

        if unique_client_counter is None:
            unique_client_counter = Client.objects.all().distinct('email')
            cache.get('unique_client_counter', unique_client_counter)
        else:
            unique_client_counter = Client.objects.all().distinct('email')

    return len(total_mail_counter), len(active_mail_counter), len(
        unique_client_counter)


def get_random_blog():
    """ Получает 3 статьи рандомно """

    items = list(Article.objects.all())
    if len(items) < 3:
        random_items = random.sample(items, len(items))
    else:
        random_items = random.sample(items, 3)
    return random_items
