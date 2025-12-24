from watson.search import SearchAdapter


class NewsAndArticleSearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.title, obj.h1])

    def get_description(self, obj):
        # return obj.short_description
        return ''

    def get_content(self, obj):
        return obj.text


class PageSearchAdapter(SearchAdapter):

    def get_title(self, obj):
        return ', '.join([obj.title, obj.h1])

    def get_description(self, obj):
        return obj.description

    def get_content(self, obj):
        return obj.text
