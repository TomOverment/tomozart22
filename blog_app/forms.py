from django import forms
from .models import Post, Comment
from django.utils.text import slugify


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'status', 'post_image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Post Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Comment here'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'post_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            }


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'status', 'post_image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Post Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Comment here'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'post_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control',
                                          'placeholder': 'Add a comment'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your Name"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Your Email"
        })
    )

    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Subject"
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Your Message"
        })
    )
