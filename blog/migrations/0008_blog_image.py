# Generated by Django 3.0.3 on 2020-04-25 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20200422_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='image',
            field=models.ImageField(null=True, upload_to='', verbose_name='Resim'),
        ),
    ]
