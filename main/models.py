from django.db import models




class GeneralUser(models.Model):
    ROLE = {
        "MAIN": "Основной чат",
        "MINI": "Мини чат",
    }

    name = models.CharField(max_length=60, null=True, blank=True, verbose_name='ФИО пользователя')
    username = models.CharField(max_length=40, null=True, blank=True, verbose_name='Никнейм')
    role = models.CharField(max_length=10, blank=True, choices=ROLE, verbose_name='Тип чата')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Основные пользователи чата'


class OtherUser(models.Model):

    name = models.CharField(max_length=30, null=True, blank=True,verbose_name='ФИО пользователя')
    username = models.CharField(max_length=40, null=True, blank=True, verbose_name='Никнейм')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Маршрутная карта'



class Region(models.Model):
    CHOICE = {
        "MIS": "МИС",
        "TFOMS": "ТФОМС"
    }

    name_region = models.CharField(max_length=30, null=True, blank=True, verbose_name='Регион')
    service = models.CharField(max_length=7, blank=True, choices=CHOICE, verbose_name='Сервис')

    def __str__(self):
        return self.name_region

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class RegionsAndUsers(models.Model):
    username = models.ForeignKey(OtherUser, verbose_name='Юзернейм', on_delete=models.PROTECT)
    region = models.ForeignKey(Region, verbose_name='Регион', on_delete=models.PROTECT)
    is_admin = models.BooleanField(default=False, verbose_name='Админ чата')


    def __str__(self):
        return self.username.name


    class Meta:
        verbose_name = 'Регион и пользователь'
        verbose_name_plural = 'Регионы и пользователи'