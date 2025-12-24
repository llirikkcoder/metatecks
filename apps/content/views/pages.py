from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from apps.content.models import Page


class PageView(TemplateView):
    template_name = 'page.html'

    def get_template_names(self, *args, **kwargs):
        slug = self.kwargs['slug']
        if slug == 'about/requisites':
            return 'about/requisites.html'
        return super().get_template_names(*args, **kwargs)

    def get_page(self):
        return get_object_or_404(Page, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = {
            'page': self.get_page(),
        }
        context.update(super().get_context_data(**kwargs))
        return context
