from django.apps import AppConfig

from watson import search

from apps.search.adapters import NewsAndArticleSearchAdapter, PageSearchAdapter


class ContentConfig(AppConfig):
    name = 'apps.content'
    verbose_name = 'Контент на сайте'

    def ready(self):
        News = self.get_model('News')
        Article = self.get_model('Article')
        Page = self.get_model('Page')

        search.register(
            News.objects.published(),
            NewsAndArticleSearchAdapter,
            store=('title',),
        )
        search.register(
            Article.objects.published(),
            NewsAndArticleSearchAdapter,
            store=('title',),
        )
        search.register(Page, PageSearchAdapter, store=('title',))
