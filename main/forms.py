from django import forms
from .models import GeneralUser


class UpdateUserRegionForm(forms.Form):
    username = forms.CharField(max_length=100, label='Ник в телеграмме', widget=forms.TextInput(attrs={'name': 'username'}))
    is_admin = forms.BooleanField(required=False, label='Права администратора',
                                  widget=forms.CheckboxInput(attrs={'name': 'is_admin'}))

    def __init__(self, *args, **kwargs):
        username_initial = kwargs.pop("username_initial", None)
        super(UpdateUserRegionForm, self).__init__(*args, **kwargs)
        if username_initial:
            self.fields["username"].initial = username_initial


class UpdateUserForm(forms.Form):
    username = forms.CharField(max_length=100, label='Ник в телеграмме', widget=forms.TextInput(attrs={'name': 'username'}))
    main = forms.BooleanField(required=False, label='Основной чат',
                                  widget=forms.CheckboxInput(attrs={'role': 'MAIN'}))
    mini = forms.BooleanField(required=False, label='Мини чат',
                              widget=forms.CheckboxInput(attrs={'role': 'MINI'}))

    def __init__(self, *args, **kwargs):
        username_initial = kwargs.pop("username_initial", None)
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        if username_initial:
            self.fields["username"].initial = username_initial


class AddUserForm(forms.Form):
    name = forms.CharField(max_length=100, label='ФИО пользователя', widget=forms.TextInput(attrs={'name': 'username'}))
    username = forms.CharField(max_length=100, label='Ник в телеграмме', widget=forms.TextInput(attrs={'name': 'username'}))
    main = forms.BooleanField(required=False, label='Основной чат',
                                  widget=forms.CheckboxInput(attrs={'role': 'MAIN'}))
    mini = forms.BooleanField(required=False, label='Мини чат',
                              widget=forms.CheckboxInput(attrs={'role': 'MINI'}))


class SearchUserForm(forms.Form):
    name = forms.CharField(max_length=100, label='Введите ФИО для поиска')


class MacrosForm(forms.Form):
    sheet = forms.CharField(max_length=100, label='Введите название листа')