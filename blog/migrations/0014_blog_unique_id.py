# Generated by Django 3.0.3 on 2020-04-25 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20200425_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='unique_id',
            field=models.CharField(editable=False, max_length=100, null=True),
        ),
    ]
