# Generated by Django 3.0.5 on 2021-03-25 12:03

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_feedbackform_quiz_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='correct_marks',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='negative_marks',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='question',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]