from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_account.constants import PASSWORD_AND_CONFIRM_PASSWORD
from user_account.models import UserProfile
from user_account.tokens import account_activation_token
from utils.helper_methods import send_mail_to_user

User = get_user_model()


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', max_length=128, required=True, widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password', max_length=128, required=True, widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'interest', 'password', 'confirm_password')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields.get('first_name').required = True
        self.fields.get('last_name').required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('password', PASSWORD_AND_CONFIRM_PASSWORD)
        return cleaned_data

    def save(self, commit=True):
        is_updated = self.instance.pk
        user = super(UserRegisterForm, self).save(commit=commit)
        if self.cleaned_data.get('password'):
            user.set_password(user.password)
        if not is_updated:
            user.is_active = False
            current_site = get_current_site(self.request)
            send_mail_to_user.apply_async(kwargs={
                'subject': 'VERIFY YOUR EMAIL',
                'to': (user.email,),
                'html_template': 'emails/user_email_verification.html',
                'context': {
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
            })
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'interest')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserDetailUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # fields = ('profile_picture', 'cover_picture', 'about', 'website', 'country', 'language')
        fields = ('about', 'website', 'country', 'language')

    def __init__(self, *args, **kwargs):
        super(UserDetailUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        context.pop('user')
        send_mail_to_user.apply_async(kwargs={
                'subject': 'PASSWORD RESET',
                'to': (to_email,),
                'html_template': email_template_name,
                'context': context
        })
