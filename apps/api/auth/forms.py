from django import forms

from apps.users.models import User


class LoginForm(forms.Form):
    """
    Форма логина
    """
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if not self._errors:
            email = cleaned_data.get('email')
            password = cleaned_data.get('password')
            try:
                user = User.objects.get(email__iexact=email)
                if not user.check_password(password):
                    raise User.DoesNotExist()
            except User.DoesNotExist:
                raise forms.ValidationError('Неверное сочетание Email / Пароль')
        return cleaned_data


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'patronymic_name', 'last_name', 'phone',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).count():
            raise forms.ValidationError('Аккаунт с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ResetPasswordForm(forms.Form):
    """
    Форма восстановления пароля
    """
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        if not self._errors:
            email = cleaned_data.get('email')
            try:
                User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise forms.ValidationError('Пользователя с таким email не существует')
        return cleaned_data
