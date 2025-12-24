from django import forms

from .models import User


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_repeat = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_admin', 'is_superuser',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email

    def clean_password_repeat(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')

        if password and password_repeat and password != password_repeat:
            raise forms.ValidationError('Пароли не совпадают')

        return password_repeat

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'

    def _clean_email(self, key):
        email = self.cleaned_data.get(key)
        if email:
            email = email.lower()
        return email

    def clean_email(self):
        return self._clean_email('email')

    def clean_contact_email(self):
        return self._clean_email('contact_email')
