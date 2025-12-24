from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from apps.catalog.models import Brand, Product
from apps.content.models import AboutCompany
from apps.media_content.models import MediaTag, MediaVideo, MediaPhoto, MediaFile


class AboutPageView(TemplateView):
    template_name = 'about/about_page.html'

    def get_data(self):
        about = AboutCompany.get_solo()

        facts = about.facts.all()
        facts1 = facts.filter(place=1)
        facts2 = facts.filter(place=2)

        advantages = about.advantages.filter(is_shown=True)
        warehouses = about.warehouses.filter(is_shown=True)[:2]
        companies = about.transport_companies.filter(is_shown=True)

        brand_ids = Product.objects.filter(is_shown=True, model__is_shown=True).values_list('brand_id', flat=True)
        brand_ids = set(brand_ids)
        brands = Brand.objects.filter(id__in=brand_ids, logo__gt='').order_by('?')

        return {
            'about': about,
            'facts1': facts1,
            'facts2': facts2,
            'advantages': advantages,
            'warehouses': warehouses,
            'companies': companies,
            'brands': brands,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data


class MediaViewBase(TemplateView):
    model = None
    with_tag = False
    model_name = ''

    def get_tag(self):
        self.tag = None
        if self.with_tag:
            self.tag = get_object_or_404(MediaTag, slug=self.kwargs['tag'])
        return self.tag

    def get_queryset(self, **kwargs):
        self.base_qs = self.qs = self.model.objects.published()
        if self.with_tag:
            tag = self.get_tag()
            self.qs = self.qs.filter(tags=tag)
        return self.qs

    def get_tags(self):
        tag_ids = self.base_qs.values_list('tags', flat=True)
        self.tags = list(MediaTag.objects.filter(id__in=tag_ids))
        if self.with_tag:
            tag = self.tag
            if tag.id not in tag_ids:
                self.tags.append(tag)
        for tag in self.tags:
            tag.url = tag.get_url(self.model_name)
        return self.tags

    def get_context_data(self, **kwargs):
        self.get_tag()
        self.get_queryset()
        self.get_tags()
        base_url = reverse(f'about:{self.model_name}')
        context = {
            'items': self.qs,
            'active_tag': self.tag,
            'tags': self.tags,
            'base_url': base_url,
        }
        context.update(super().get_context_data(**kwargs))
        return context


class VideoView(MediaViewBase):
    template_name = 'about/video.html'
    model = MediaVideo
    model_name = 'video'
    with_tag = False


class PhotoView(MediaViewBase):
    template_name = 'about/photo.html'
    model = MediaPhoto
    model_name = 'photo'
    with_tag = False


class FilesView(MediaViewBase):
    template_name = 'about/files.html'
    model = MediaFile
    model_name = 'files'
    with_tag = False
