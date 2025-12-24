from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import TemplateView

from watson import search


class SearchPageView(TemplateView):
    template_name = 'search.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('query')
        if not self.query:
            return HttpResponseRedirect(reverse('home'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        results = search.search(self.query)
        context = {
            'results': results,
        }
        context.update(super().get_context_data(**kwargs))
        return context
