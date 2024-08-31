from django.db import models
from datetime import datetime
from config import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    first_name = models.CharField(max_length=100, **NULLABLE,
                                  verbose_name='фамилия')
    last_name = models.CharField(max_length=100, **NULLABLE,
                                 verbose_name='имя')
    surname = models.CharField(max_length=100, **NULLABLE,
                               verbose_name='отчество')
    email = models.EmailField(max_length=100, verbose_name='email')
    comment = models.TextField(blank=True, verbose_name='комментарий')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, **NULLABLE,
                             related_name='create_client',
                             verbose_name='добавил клиента')

    def __str__(self):
        return (f'{self.first_name} {self.last_name} {self.surname} -'
                f' {self.email}')

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'


class MailSettings(models.Model):
    STATUS_CREATED = 'created'
    STATUS_IN_PROCESS = 'in_process'
    STATUS_FINISHED = 'finished'

    STATUSES = (
        (STATUS_CREATED, 'Создано'),
        (STATUS_IN_PROCESS, 'В процессе'),
        (STATUS_FINISHED, 'Завершена'),
    )

    PERIOD_DAILY = 'day'
    PERIOD_WEEKLY = 'week'
    PERIOD_MONTHLY = 'month'

    PERIOD_CHOICES = (
        ('day', 'Раз в день'), ('week', 'Раз в неделю'),
        ('month', 'Раз в месяц'))
    STATUS_CHOICES = (('create', 'Создана'), ('in_process', 'Запущена'),
                      ('finished', 'Завершена'))

    message = models.ForeignKey('Message', on_delete=models.CASCADE,
                                verbose_name='Сообщение')
    start_time = models.DateTimeField(verbose_name='Время начала рассылки', default=datetime.now())
    end_time = models.DateTimeField(verbose_name='Время окончания', **NULLABLE)
    period = models.CharField(max_length=50, choices=PERIOD_CHOICES,
                              verbose_name='Периодичность рассылки')
    client = models.ManyToManyField(Client, related_name="get_client",
                                    verbose_name='Клиент')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='in_process', verbose_name='Статус '
                                                                 'рассылки')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, **NULLABLE,
                             related_name='create_mail',
                             verbose_name='Добавил рассылку')

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        permissions = [('set_status', 'Can deactivate mail')]


class Message(models.Model):
    title = models.CharField(max_length=150, verbose_name='заголовок')
    message = models.TextField(**NULLABLE, verbose_name='сообщение')

    def __str__(self):
        return f'{self.title} ({self.message})'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'


class Logs(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUSES = (
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    )

    last_try = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата последней попытки')
    status = models.CharField(choices=STATUSES, default=STATUS_SUCCESS,
                              verbose_name='статус')
    answer_server = models.TextField(verbose_name='ответ сервера', **NULLABLE)
    mail = models.ForeignKey(MailSettings, on_delete=models.CASCADE,
                                 related_name="get_log",
                                 verbose_name='рассылка')

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'