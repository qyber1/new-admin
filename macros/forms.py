from django import forms


class MacrosForm(forms.Form):
    sheet = forms.CharField(max_length=100, label='Введите название листа')