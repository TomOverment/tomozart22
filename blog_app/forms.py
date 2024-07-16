from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author', 'content', 'slug', 'status', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'author': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment here'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author', 'content', 'status', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post Title'}),
            'author': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comment here'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment'}),
        }


