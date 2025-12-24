from django import forms
from django.core.files.images import get_image_dimensions

from .models import Banner


class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = '__all__'

    # def _check_image(self, image, min_width, min_height):
    #     w, h = get_image_dimensions(image)
    #     w_err = w < min_width
    #     h_err = h < min_height

    #     if w_err and h_err:
    #         raise forms.ValidationError(
    #             f'Размеры изображения {w}x{h}px, хотя должны быть не меньше {min_width}x{min_height}px'
    #         )
    #     elif w_err:
    #         raise forms.ValidationError(
    #             f'Ширина изображения {w}px, хотя должна быть не меньше {min_width}px'
    #         )
    #     elif h_err:
    #         raise forms.ValidationError(
    #             f'Высота изображения {h}px, хотя должна быть не меньше {min_height}px'
    #         )

    # def clean_image_1200(self):
    #     """
    #     >= 1200х570px
    #     """
    #     image = self.cleaned_data.get('image_1200')
    #     if self.instance.id and image == Banner.objects.get(id=self.instance.id).image_1200:
    #         return image
    #     if image:
    #         self._check_image(image, 1200, 570)
    #     return image

    # def clean_image_670(self):
    #     """
    #     >= 670х950px
    #     """
    #     image = self.cleaned_data.get('image_670')
    #     if self.instance.id and image == Banner.objects.get(id=self.instance.id).image_670:
    #         return image
    #     if image:
    #         self._check_image(image, 670, 950)
    #     return image
