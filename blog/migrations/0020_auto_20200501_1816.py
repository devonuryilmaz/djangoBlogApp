# Generated by Django 2.2.3 on 2020-05-01 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_auto_20200501_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yorum',
            name='blog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='blog.Blog'),
        ),
    ]
