# Generated by Django 3.0.5 on 2021-04-10 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_merge_20210331_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackform',
            name='username',
            field=models.CharField(default='', max_length=60),
        ),
    ]
