from watson.search import SearchAdapter


class CategorySearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.name, obj.name_plural, obj.name_single, obj.name_product, obj.h1])

    def get_description(self, obj):
        return ''

    def get_content(self, obj):
        return ''


class SubCategorySearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.name, obj.name_single, obj.h1])

    def get_description(self, obj):
        return ', '.join([obj.purpose, obj.description])

    def get_content(self, obj):
        return ', '.join([obj.design_features, obj.construction_features])


class ProductSearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.name, obj.h1])

    def get_description(self, obj):
        return obj.model.description

    def get_content(self, obj):
        return obj.model.tech_description


class BrandSearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.name, obj.h1])

    def get_description(self, obj):
        return obj.description

    def get_content(self, obj):
        return obj.text
