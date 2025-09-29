# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(strip=False,
                                widget=forms.PasswordInput(attrs={'class': 'form-control','required': True}))        
    password2 = forms.CharField(strip=False,
                                widget=forms.PasswordInput(attrs={'class': 'form-control','required': True}))
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'required': True,
            'autocomplete': 'email',
            'placeholder': 'Enter a valid email address'
        }),
        error_messages={
            "invalid": "Please enter a valid email address."
        }
    )
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control','required': True,'placeholder': 'Enter a username'}),
            "email": forms.EmailInput(attrs={'class': 'form-control','required': True,"autocomplete": "email"}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].widget.attrs.pop("autofocus", None)

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets ={
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
            }),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.pop('autofocus', None)


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control','placeholder': 'Enter your username','id':'username'})
        self.fields['password'].widget.attrs.update({'class':'form-control','placeholder': 'Enter your password','id':'password'})

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )