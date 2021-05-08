from django import forms
from ckeditor_uploader.fields import RichTextUploadingField
from .models import *

class QuestionForm(forms.ModelForm):
    answer = forms.IntegerField(required=False)
    text = forms.CharField(max_length=10000, required=False)

    class Meta:
        model = Question
        fields = [
            'answer',
            'text',
            'correct_marks',
            'negative_marks',
            
        ]

        labels = {
            'answer': 'Write option number of answer',
            'marks': 'marks',
            'negative_mark': 'negative mark',


        }