from django import forms

from .models import ProductModel, Product


class ProductModelForm(forms.ModelForm):

    class Meta:
        model = ProductModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # настройка полей с галереями
        self.fields['gallery'].required = False
        self.fields['gallery'].max_number_of_images = 5
        self.fields['gallery_3d'].required = False

        # добавление динамических полей с характеристиками
        obj = self.instance
        attrs = obj.attrs
        self.fields_dict = {}

        if obj and obj.id:
            # - берем список полей
            # sub_category = obj.sub_category
            # self.fields_dict = sub_category.get_attrs_fields()
            self.fields_dict = obj.get_attrs_fields()

            for name, field in self.fields_dict.items():
                # - добавляем поле
                self.fields[name] = field
                # - проставляем текущее значение
                _name = name.split('attrs__', 1)[1]
                _value = obj.attrs.get(_name)
                field.initial = _value

    def save(self, commit=True):
        """
        Сохраняем данные из динамических полей в поле attrs у объекта
        """
        obj = super().save(commit=False)
        obj.attrs = {}
        for name, field in self.fields_dict.items():
            value = self.cleaned_data.get(name)
            if value not in [None, '']:
                _name = name.split('attrs__', 1)[1]
                _value = (
                    int(value)
                    if hasattr(self.fields[name], 'choices')
                    else value
                )
                obj.attrs[_name] = _value
        if commit:
            obj.save()
        return obj


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # настройка полей с галереями
        self.fields['gallery'].required = False
        self.fields['gallery'].max_number_of_images = 5
        self.fields['gallery_3d'].required = False
