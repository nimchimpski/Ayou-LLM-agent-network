# Generated by Django 4.2.3 on 2023-07-27 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ayou', '0003_biographyitem_user_chat_user_memory_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memory',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]