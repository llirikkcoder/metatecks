from django import forms

from .models import AboutAdvantage


class AboutAdvantageForm(forms.ModelForm):

    class Meta:
        model = AboutAdvantage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gallery'].required = False
