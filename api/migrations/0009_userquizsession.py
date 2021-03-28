# Generated by Django 3.0.5 on 2021-03-26 05:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0008_auto_20210325_1733'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuizSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('remaining_duration', models.TimeField(blank=True, null=True)),
                ('quiz_id', models.ForeignKey(default='4f3b3f6b-e1d0-4ca9-986b-1ec66aae968f', on_delete=django.db.models.deletion.CASCADE, to='api.Quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
