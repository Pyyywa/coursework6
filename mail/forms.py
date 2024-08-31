from django import forms

from mail.models import Message, Client, MailSettings


class FormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "is_active" and field_name != "client":
                field.widget.attrs["class"] = "form-control"


class ContactForm(FormMixin, forms.Form):
    """
    Форма для контактов.
    """

    name = forms.CharField(label="Имя", max_length=255)
    email = forms.EmailField(label="Email")
    content = forms.CharField(
        label="Сообщение", widget=forms.Textarea(attrs={"cols": 60, "rows": 10})
    )


class MessageForm(FormMixin, forms.ModelForm):
    """
    Форма для создания и редактирования сообщения рассылки
    """

    class Meta:
        model = Message
        fields = "__all__"


class ClientForm(FormMixin, forms.ModelForm):
    """
    Форма для добавления и редактирования клиента
    """

    class Meta:
        model = Client
        exclude = ("user",)


class MailSettingsForm(FormMixin, forms.ModelForm):
    """
    Форма для создания и редактирования настроек рассылки.
    """

    class Meta:
        model = MailSettings
        exclude = ("user", "status")
        help_texts = {
            "start_time": "Дата и время в формате: ДД.ММ.ГГГГ ЧЧ:ММ",
            "end_time": "Дата и время в формате: ДД.ММ.ГГГГ ЧЧ:ММ",
        }
        widgets = {
            "message": forms.Select,
            "client": forms.CheckboxSelectMultiple,
        }


class MailSettingsChangeStatus(FormMixin, forms.ModelForm):
    """
    Форма для изменения статуса рассылки
    """

    class Meta:
        model = MailSettings
        fields = ("status",)
