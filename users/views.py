from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, \
    UserPassesTestMixin, PermissionRequiredMixin

from .models import User
from .forms import UserRegisterForm, UserProfileForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login


class LetterSending(TemplateView):
    template_name = 'users/success_letter.html'
    extra_context = {
        'title': 'Завершение регистрации'
    }


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:letter_sending')
    template_name = 'users/register.html'

    def form_valid(self, form):
        self.object = form.save()
        self.object.is_active = False
        self.object.verification_key = User.objects.make_random_password()
        self.object.save()
        send_mail(
            subject='Регистрация',
            message=f'Вы зарегистрировались на нашем сайте. Для подтверждения '
                    f'регистрации перейдите по ссылке: '
                    f'http://127.0.0.1:8000/users/verification/'
                    f'{self.object.verification_key}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.object.email]
        )
        return super().form_valid(form)


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=False)
        return queryset


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    permission_required = 'users.set_is_active'
    fields = ['is_active', ]


def verify_email_view(request, key):
    if request.method == 'GET':
        user = User.objects.get(verification_key=key)
        user.is_active = True
        user.save()

        context = {
            'object_list': User.objects.filter(verification_key=key)
        }
    login(request, user)
    return render(request, 'users/verification.html', context)


def password_reset_view(request):
    if request.method == 'POST':
        user = User.objects.get(email=request.POST.get('email'))
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        send_mail(
            subject='Сброс пароля',
            message=f'Вы запросили сброс пароля. Ваш новый пароль: '
                    f'{new_password}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.POST.get('email')]
        )
        return redirect('users:login')

    return render(request, 'users/reset_password.html')
