from django.db import models
from mail.models import NULLABLE


class Article(models.Model):
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    body = models.TextField(verbose_name='Содержимое')
    date_create = models.DateField(auto_now_add=True,
                                   verbose_name='Дата создания')
    preview = models.ImageField(upload_to='blog/', **NULLABLE,
                                verbose_name='Изображение')
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликована или нет')
    views_count = models.IntegerField(default=0,
                                      verbose_name='Количество просмотров')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'
