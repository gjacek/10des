from django import forms
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'edition', 'is_visible']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'is_visible': forms.CheckboxInput(attrs={'role': 'switch'}),
        }

class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'is_published': forms.CheckboxInput(attrs={'role': 'switch'}),
        }

class LessonUpdateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'is_published': forms.CheckboxInput(attrs={'role': 'switch'}),
        }
