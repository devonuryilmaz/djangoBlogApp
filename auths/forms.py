from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile
import re


class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=5, required=True, label="Password",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(min_length=5, required=True, label="Password Confirm",
                                       widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username',
                  'email', 'password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password != password_confirm:
            self.add_error('password', 'Parololar Eşleşmiyor.')
            self.add_error('password_confirm', 'Parololar Eşleşmiyor.')

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu email sistemde kayıtlı')
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu kullanıcı adı sistemde mevcut.')
        return username


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=50, label="Username",
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, max_length=50, label="Password",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError(
                '<b>Hatalı kullanıcı adı veya şifre girildi!</b>')

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            users = User.objects.filter(email__iexact=username)
            if len(users) > 0 and len(users) == 1:
                return users.first().username
        return username


class UserProfileUpdateForm(forms.ModelForm):

    sex = forms.ChoiceField(required=True, choices=UserProfile.SEX)
    profile_photo = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    dogum_tarihi = forms.DateField(
        widget=forms.DateInput(format='%d.%m.%Y'), required=True, label="Doğum Tarihi", input_formats=('%d.%m.%Y', ))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'dogum_tarihi',
                  'profile_photo', 'email', 'bio', 'sex']

    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['bio'].widget.attrs['rows'] = 10
        DATEPICKER = {
            'type': 'text',
            'class': 'form-control',
            'autocomplete': 'off'
        }
        self.fields['dogum_tarihi'].widget.attrs.update(DATEPICKER)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Lütfen email giriniz")

        if User.objects.filter(email=email).exclude(username=self.instance.username).exists():
            raise forms.ValidationError("Bu mail adresi kayıtlıdır!")

        return email


class UserPasswordChangeForm(forms.Form):
    user = None
    password = forms.CharField(required=True, min_length=4, label="Mevcut Şifre",
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(required=True, min_length=4, label="Yeni Şifre",
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password_confirm = forms.CharField(
        required=True, min_length=4, label="Yeni Şifre Doğrulama", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_confirm = self.cleaned_data.get('new_password_confirm')

        if new_password != new_password_confirm:
            self.add_error('new_password', 'Yeni girilen şifreler eşleşmiyor.')
            self.add_error('new_password_confirm',
                           'Yeni girilen şifreler eşleşmiyor.')

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not self.user.check_password(password):
            raise forms.ValidationError('Lütfen şifrenizi doğru giriniz.')

        return password


class PasswordChangeForm2(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeForm2, self).__init__(user, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
