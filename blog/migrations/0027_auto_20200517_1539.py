# Generated by Django 2.2.3 on 2020-05-17 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0026_favoriteblog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriteblog',
            options={'verbose_name_plural': 'Favorilere Eklenen Gönderiler'},
        ),
    ]