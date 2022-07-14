from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': "form-control"}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'class': "form-control"}),
        strip=False,
    )
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", 'class': "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
        widgets = {
            'username':forms.TextInput(attrs={'class':'form-control'}),
        }



class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
