from django.views.generic import ListView, UpdateView, DeleteView, \
    CreateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, Http404

from mail.forms import ContactForm, ClientForm, MailSettingsForm, \
    MailSettingsChangeStatus, MessageForm
from mail.models import Client, MailSettings, Message, Logs
from mail.services import get_cached_data, get_random_blog


class IndexView(TemplateView):
    """ Главная страница """

    template_name = 'mail/index.html'

    def get_context_data(self):
        total_mail_counter = get_cached_data()[0]
        active_mail_counter = get_cached_data()[1]
        unique_client_counter = get_cached_data()[2]
        context = {
            'title': 'Главная',
            'total_mail_counter': total_mail_counter,
            'active_mailing_counter': active_mail_counter,
            'unique_client_counter': unique_client_counter,
            'random_blog': get_random_blog() if get_random_blog() else [],
        }

        return context


class ContactFormView(FormView):
    """ Контактная информация и отправка сообщения """

    form_class = ContactForm
    template_name = 'mail/contact.html'
    success_url = reverse_lazy('/')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Свяжитесь с нами:'
        return context

    def form_valid(self, form):
        if form.is_valid():
            print(form.cleaned_data)
        return redirect('/')


###############################################################################
class ClientListView(LoginRequiredMixin, ListView):
    """ Список клиентов, доступны к просмотру клиенты, созданные
    пользователем"""

    model = Client

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset


class ClientCreateView(LoginRequiredMixin, CreateView):
    """ Создание клиента """

    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mail:clients')

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """ Редактирование клиента, доступны к редактированию клиенты, созданные
    пользователем"""

    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mail:clients')

    def form_valid(self, form):
        if not self.request.user.is_staff:
            form.instance.user = self.request.user
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """ Удаление клиента, доступны к удалению клиенты, созданные
    пользователем"""

    model = Client
    success_url = reverse_lazy('mail:clients')


###############################################################################
class MailSettingsListView(LoginRequiredMixin, ListView):
    """ Список рассылок, созданных пользователем """

    model = MailSettings

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


class MailSettingsCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                             CreateView):
    """ Создание рассылки """

    model = MailSettings
    form_class = MailSettingsForm
    permission_required = 'mail.add_mailsettings'
    success_url = reverse_lazy('mail:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            form.fields['client'].queryset = Client.objects.filter(
                user=self.request.user)
        else:
            form.fields['client'].queryset = Client.objects.all()
        return form

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)


class MailSettingsUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                             UpdateView):
    """ Редактирование рассылки, доступны к редактированию рассылки,
    созданные пользователем"""

    model = MailSettings
    form_class = MailSettingsForm
    permission_required = 'mail.change_mailsettings'
    success_url = reverse_lazy('mail:list')

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user and not self.request.user.is_staff:
            raise Http404

        return self.object


class MailSettingsDeleteView(LoginRequiredMixin, PermissionRequiredMixin,
                             DeleteView):
    """ Удаление рассылки """

    model = MailSettings
    permission_required = 'mail.delete_mailsettings'
    success_url = reverse_lazy('mail:list')

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['clients'] = Client.objects.all()
        context_data['mail_pk'] = self.kwargs.get('pk')

        return context_data


class StatusmailettingsUpdateView(LoginRequiredMixin,
                                      PermissionRequiredMixin, UpdateView):
    model = MailSettings
    form_class = MailSettingsChangeStatus
    success_url = reverse_lazy('mail:list')
    permission_required = 'mail.set_status'


###############################################################################
class MessageListView(LoginRequiredMixin, ListView):
    """ Список сообщений, доступно для использования всем """

    model = Message


class MessageCreateView(LoginRequiredMixin, CreateView):
    """ Создание сообщения для рассылок """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mail:message_list')


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
                        UpdateView):
    """ Редактирование сообщения для рассылок """

    model = Message
    form_class = MessageForm
    permission_required = 'mail.change_message'
    success_url = reverse_lazy('mail:message_list')


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin,
                        DeleteView):
    """ Удаление сообщения для рассылок """

    model = Message
    permission_required = 'mail.delete_message'
    success_url = reverse_lazy('mail:message_list')


###############################################################################
class MailingLogListView(LoginRequiredMixin, ListView):
    """ Список логов по рассылке """

    model = Logs

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = Logs.objects.filter(
            mail=self.kwargs.get('pk')).order_by(
            '-last_try')
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['mail'] = MailSettings.objects.get(
            pk=self.kwargs.get('pk'))
        return context_data