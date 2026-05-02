from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ProfileUpdateForm(forms.ModelForm):
    lastLogin = forms.DateTimeField(
        label='Last login',
        required=False,
        disabled=True
    )

    dateJoined = forms.DateTimeField(
        label='Date joined',
        required=False,
        disabled=True,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'lastLogin', 'dateJoined')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['lastLogin'].initial = self.instance.last_login
            self.fields['dateJoined'].initial = self.instance.date_joined

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email != self.instance.email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('An account already exists for this email address!')

        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label='Repeat new password',
        widget=forms.PasswordInput()
    )
