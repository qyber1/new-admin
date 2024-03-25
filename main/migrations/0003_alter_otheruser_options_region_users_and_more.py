# Generated by Django 5.0.3 on 2024-03-10 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_regions_region_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='otheruser',
            options={'verbose_name': 'Пользователь маршрутной карты', 'verbose_name_plural': 'Пользователи маршрутной карты'},
        ),
        migrations.AddField(
            model_name='region',
            name='users',
            field=models.ManyToManyField(to='main.otheruser'),
        ),
        migrations.DeleteModel(
            name='RegionsAndUser',
        ),
    ]
