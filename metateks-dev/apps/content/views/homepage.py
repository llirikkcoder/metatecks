from django.views.generic import TemplateView

from apps.banners.models import Banner
from apps.catalog.models import Brand, Category, SubCategory, Product
from apps.content.models import Homepage, News, Article
from apps.media_content.models import MediaPhoto, MediaVideo


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_data(self):
        home = Homepage.get_solo()

        categories = Category.objects.filter(is_shown=True)

        banners = Banner.objects.published().filter(banner_place='homepage')
        banners_count = banners.count()

        sub_categories = SubCategory.objects.select_related('category').prefetch_related('models')\
                                            .filter(is_popular=True).order_by('?')[:7]
        sub_categories = list(sub_categories)
        for s in sub_categories:
            model1 = s.models.filter(photo__gt='').first()
            model2 = s.models.filter(price__gt=0).order_by('price').first()
            s.model_photo_url = model1.list_photo_url if model1 else s.product_photo_url
            s.model_price = model2.price if model2 else None

        news_post = News.objects.filter(is_published=True).first()
        articles = Article.objects.filter(is_published=True)[:2]
        photos = MediaPhoto.objects.filter(is_published=True)[:4]
        video = MediaVideo.objects.filter(is_published=True).exclude(video__startswith='http').first()

        brand_ids = Product.objects.filter(is_shown=True, model__is_shown=True).values_list('brand_id', flat=True)
        brand_ids = set(brand_ids)
        brands = Brand.objects.filter(id__in=brand_ids, logo__gt='').order_by('?')

        warehouses = home.warehouses.all()
        warehouses_count = warehouses.count()
        wh1 = warehouses[0] if warehouses_count > 0 else None
        wh2 = warehouses[1] if warehouses_count > 1 else None

        return {
            'home': home,
            'categories': categories,
            'sub_categories': sub_categories,
            'banners': banners,
            'banners_count': banners_count,
            'news_post': news_post,
            'articles': articles,
            'photos': photos,
            'video': video,
            'brands': brands,
            'wh1': wh1,
            'wh2': wh2,
        }

    def get_context_data(self, **kwargs):
        data = self.get_data()
        data.update(super().get_context_data(**kwargs))
        return data
