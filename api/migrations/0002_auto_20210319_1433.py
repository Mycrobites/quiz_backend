# Generated by Django 3.0.5 on 2021-03-19 09:03

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizassign',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='quizassign',
            name='response',
            field=jsonfield.fields.JSONField(blank=True),
        ),
    ]
