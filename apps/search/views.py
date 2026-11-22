from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import ListView

from watson import search


class SearchPageView(ListView):
    template_name = 'search.html'
    paginate_by = 20
    context_object_name = 'results'

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('query')
        if not self.query:
            return HttpResponseRedirect(reverse('home'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return search.search(self.query).order_by("-watson_rank", "pk")
