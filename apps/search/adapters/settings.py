from watson.search import SearchAdapter


class SEOSettingSearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.description, obj.h1])

    def get_description(self, obj):
        return obj.header_text

    def get_content(self, obj):
        return ''
