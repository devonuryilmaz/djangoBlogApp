# Generated by Django 2.2.3 on 2020-05-01 00:01

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20200425_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='icerik',
            field=ckeditor.fields.RichTextField(max_length=1000, null=True, verbose_name='İçerik Giriniz'),
        ),
    ]
