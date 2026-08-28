import re

from django import forms

from apps.feedback.models import CallbackRequest


class CallbackForm(forms.ModelForm):
    phone = forms.CharField(label='Телефон')

    class Meta:
        model = CallbackRequest
        fields = ('name', 'phone',)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError('Укажите корректный номер телефона')
        return phone
