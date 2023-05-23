from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ClearableFileInput

from course.models import User, Comment


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "image", "password1", "password2"]


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "block border border-grey-light w-full p-3 rounded mb-4",
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "class": "block border border-grey-light w-full p-3 rounded mb-4",
                "placeholder": "Password",
            }
        )
    )


class CommentCourseFrom(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
