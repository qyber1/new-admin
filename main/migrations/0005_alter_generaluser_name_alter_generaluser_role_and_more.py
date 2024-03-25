# Generated by Django 5.0.3 on 2024-03-18 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_region_users_regionsandusers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generaluser',
            name='name',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='ФИО пользователя'),
        ),
        migrations.AlterField(
            model_name='generaluser',
            name='role',
            field=models.CharField(blank=True, choices=[('Основной', 'Основной'), ('Мини', 'Мини')], max_length=10, verbose_name='Тип чата'),
        ),
        migrations.AlterField(
            model_name='generaluser',
            name='username',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Никнейм'),
        ),
        migrations.AlterField(
            model_name='otheruser',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='ФИО пользователя'),
        ),
        migrations.AlterField(
            model_name='otheruser',
            name='username',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Никнейм'),
        ),
        migrations.AlterField(
            model_name='region',
            name='name_region',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Регион'),
        ),
        migrations.AlterField(
            model_name='region',
            name='service',
            field=models.CharField(blank=True, choices=[('МИС', 'Мис'), ('ТФОМС', 'Тфомс')], max_length=7, verbose_name='Сервис'),
        ),
    ]