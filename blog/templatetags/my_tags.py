from django import template
from users.models import User
from django.conf import settings

register = template.Library()


@register.simple_tag
def mediapath(image_path):
    if image_path:
        return f"{settings.MEDIA_URL}{image_path}"
    return '#'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.inclusion_tag('users/not_found_user.html')
def get_user(email=None):
    if not email:
        return 'Пользователь с указанным email не найден'
    else:
        user = User.objects.get(email='email')
        return {'user': user}
