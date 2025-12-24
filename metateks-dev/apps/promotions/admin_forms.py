from django import forms
from django.db.models import Q

from apps.catalog.models import Product
from .models import Promotion


class PromotionForm(forms.ModelForm):

    class Meta:
        model = Promotion
        fields = '__all__'

    def clean_product(self):
        model = self.cleaned_data.get('model')
        product = self.cleaned_data.get('product')
        if not (model or product):
            raise forms.ValidationError('Необходимо выбрать или модель, или товар')
        if model and product:
            raise forms.ValidationError('Необходимо выбрать или модель, или товар')
        return product

    def clean(self):
        data = self.cleaned_data
        if data['is_active']:
            _start = data.get('start_dt'); _end = data.get('end_dt')
            qs = Promotion.objects.filter(is_active=True)
            if self.instance.id:
                qs = qs.exclude(id=self.instance.id)

            if _end:
                qs = qs.filter(
                    (Q(start_dt__lte=_start) & Q(end_dt__gte=_start))
                    | (Q(end_dt__gte=_start) & Q(end_dt__lte=_end))
                )
            else:
                qs = qs.filter(
                    Q(end_dt__isnull=True)
                    | (Q(start_dt__lte=_start) & Q(end_dt__gte=_start))
                )

            if qs:
                _model = data.get('model')
                _product = data.get('product')
                products = (
                    [_product] if _product
                    else _model.products.all() if _model
                    else []
                )
                products = set(products)

                other_product_ids = qs.values_list('product_id', flat=True)
                other_model_ids = qs.values_list('model_id', flat=True)
                other_products = Product.objects.filter(Q(id__in=other_product_ids)|Q(model_id__in=other_model_ids))
                other_products = set(other_products)

                if _model and _model.id in other_model_ids:
                    raise forms.ValidationError(f'Дата акции для модели пересекается с другой акцией')

                bad_products = products & other_products
                if bad_products:
                    raise forms.ValidationError(f'Дата акции для товара пересекается с другими акциями')
