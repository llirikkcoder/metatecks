"""
Фиды Яндекс YML (yml_catalog) для Яндекс Директ / товарной галереи.

Три фида:
- products    — все товары (цена модели, фото как в карточке товара);
- models      — модели (название и цена модели, фото модели);
- models_work — модели, но фото берутся из подкатегории («фото в работе»).

Здесь только сборка XML; view с кэшем — в views/feeds.py.
"""
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from html import unescape

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.encoding import iri_to_uri

from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from apps.catalog.models import Category, SubCategory, Product, ProductModel, ProductPhoto


SHOP_NAME = 'Метатэкс'
SHOP_COMPANY = 'ООО «Метатэкс-маркет»'
MAX_PICTURES = 10
MAX_DESCRIPTION = 3000
SUBCATEGORY_ID_OFFSET = 1_000_000  # чтобы id подкатегорий не пересекались с id категорий

FEED_PRODUCTS = 'products'
FEED_MODELS = 'models'
FEED_MODELS_WORK = 'models_work'

_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
_SPACES_RE = re.compile(r'\s+')


def get_base_url():
    scheme = settings.DEFAULT_SCHEME
    host = settings.DEFAULT_SITENAME
    if not host.startswith(('localhost', '127.0.0.1')):
        scheme = 'https'
    return f'{scheme}://{host}'


def clean_text(value):
    return _CTRL_RE.sub('', value or '')


def plain_text(html, limit=MAX_DESCRIPTION):
    text = unescape(strip_tags(html or '')).replace('\xa0', ' ')
    text = _SPACES_RE.sub(' ', clean_text(text)).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0].rstrip() + '…'
    return text


def format_price(price):
    price = Decimal(price)
    return str(int(price)) if price == price.to_integral_value() else f'{price:.2f}'


class FeedBuilder:

    def __init__(self, kind, base_url=None):
        assert kind in (FEED_PRODUCTS, FEED_MODELS, FEED_MODELS_WORK)
        self.kind = kind
        self.base = base_url or get_base_url()
        self._model_gallery_cache = {}
        self._subcat_photos_cache = {}

    # -- url

    def abs_path(self, path):
        return self.base + iri_to_uri(path)

    def thumb(self, image, alias):
        if not image:
            return None
        try:
            url = thumbnail_url(image, alias)
        except Exception:
            return None
        if not url:
            return None
        if url.startswith('http'):
            return url
        return self.base + (url if url.startswith('/') else '/' + url)

    # -- фото

    def gallery_urls(self, gallery):
        """Фото из GalleryField в том же порядке, что и в карточке (product_gallery_big)."""
        if not gallery:
            return []
        try:
            images = list(gallery.objects.all())
        except Exception:
            return []
        urls = []
        for img in images:
            url = self.thumb(getattr(img, 'image', None), 'product_gallery_big')
            if url:
                urls.append(url)
        return urls

    def model_gallery_urls(self, model):
        if model.pk not in self._model_gallery_cache:
            urls = self.gallery_urls(model.gallery)
            if not urls:
                single = self.thumb(model.photo, 'product_gallery_big')
                urls = [single] if single else []
            self._model_gallery_cache[model.pk] = urls
        return self._model_gallery_cache[model.pk]

    def product_photos(self, product):
        """Как в карточке: галерея товара или модели -> фото товара/модели."""
        urls = self.gallery_urls(product.gallery) or self.model_gallery_urls(product.model)
        if not urls:
            single = self.thumb(product.get_photo(), 'product_gallery_big')
            urls = [single] if single else []
        return urls

    def subcategory_photos(self, sub_category):
        """
        «Фото в работе»: фото оборудования на странице подкатегории
        (ProductPhoto моделей подкатегории, как блок «Фотографии оборудования»),
        иначе — обложка подкатегории (или категории).
        """
        sid = sub_category.pk
        if sid not in self._subcat_photos_cache:
            qs = ProductPhoto.objects.filter(
                photo__gt='', is_shown=True, show_on_subcategory=True,
                model__sub_category_id=sid, model__is_shown=True,
            ).order_by('model__order', 'model_id', 'order', 'id')
            urls = []
            for p in qs[:MAX_PICTURES * 3]:
                url = self.thumb(p.photo, 'product_photos_big')
                if url and url not in urls:
                    urls.append(url)
                if len(urls) >= MAX_PICTURES:
                    break
            if not urls:
                cover = self.thumb(sub_category.get_photo(), 'sub_category_photo')
                urls = [cover] if cover else []
            self._subcat_photos_cache[sid] = urls
        return self._subcat_photos_cache[sid]

    # -- xml

    @staticmethod
    def _sub(parent, tag, text=None, **attrs):
        el = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})
        if text is not None:
            el.text = clean_text(str(text))
        return el

    def _add_offer(self, offers, *, offer_id, available, url, price, category_id, pictures, name, vendor, description):
        pictures = list(dict.fromkeys(pictures))[:MAX_PICTURES]
        if not pictures or not price or price <= 0 or not name:
            return False
        o = self._sub(offers, 'offer', id=offer_id, available='true' if available else 'false')
        self._sub(o, 'url', url)
        self._sub(o, 'price', format_price(price))
        self._sub(o, 'currencyId', 'RUR')
        self._sub(o, 'categoryId', category_id)
        for pic in pictures:
            self._sub(o, 'picture', pic)
        self._sub(o, 'name', name)
        if vendor:
            self._sub(o, 'vendor', vendor)
        if description:
            self._sub(o, 'description', description)
        return True

    def _shown_filter(self):
        return dict(
            is_shown=True,
            sub_category__is_shown=True,
            category__is_shown=True,
        )

    def build(self, now=None):
        now = now or datetime.now()
        root = ET.Element('yml_catalog', date=now.strftime('%Y-%m-%d %H:%M'))
        shop = ET.SubElement(root, 'shop')
        self._sub(shop, 'name', SHOP_NAME)
        self._sub(shop, 'company', SHOP_COMPANY)
        self._sub(shop, 'url', self.base + '/')
        currencies = ET.SubElement(shop, 'currencies')
        self._sub(currencies, 'currency', id='RUR', rate='1')
        categories_el = ET.SubElement(shop, 'categories')
        offers_el = ET.SubElement(shop, 'offers')

        used_cats = set()
        if self.kind == FEED_PRODUCTS:
            used_cats = self._build_products(offers_el)
        else:
            used_cats = self._build_models(offers_el)

        self._build_categories(categories_el, used_cats)
        ET.indent(root)
        return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='utf-8')

    def _build_categories(self, parent, used_subcat_ids):
        subs = list(
            SubCategory.objects.filter(is_shown=True, category__is_shown=True, pk__in=used_subcat_ids)
            .select_related('category').order_by('category__order', 'category_id', 'order', 'pk')
        )
        seen_cats = set()
        for sub in subs:
            if sub.category_id not in seen_cats:
                seen_cats.add(sub.category_id)
                self._sub(parent, 'category', sub.category.name, id=sub.category_id)
        for sub in subs:
            self._sub(
                parent, 'category', sub.name,
                id=sub.pk + SUBCATEGORY_ID_OFFSET, parentId=sub.category_id,
            )

    def _build_products(self, offers):
        qs = (
            Product.objects.filter(model__is_shown=True, **self._shown_filter())
            .select_related('model', 'sub_category', 'category', 'brand')
            .order_by('pk')
        )
        used = set()
        for p in qs.iterator(chunk_size=500):
            ok = self._add_offer(
                offers,
                offer_id=p.pk,
                available=p.is_in_stock,
                url=self.abs_path(p.get_absolute_url()),
                price=p.price,
                category_id=p.sub_category_id + SUBCATEGORY_ID_OFFSET,
                pictures=self.product_photos(p),
                name=p.name,
                vendor=p.brand.name if p.brand_id else (p.brand_name or None),
                description=plain_text(p.model.description),
            )
            if ok:
                used.add(p.sub_category_id)
        return used

    def _build_models(self, offers):
        qs = (
            ProductModel.objects.filter(price__gt=0, **self._shown_filter())
            .select_related('sub_category', 'category')
            .order_by('pk')
        )
        # наличие и бренд моделей — одним запросом по товарам
        stock, brands = {}, {}
        prod_qs = Product.objects.filter(is_shown=True, model__is_shown=True).values_list(
            'model_id', 'is_in_stock', 'brand__name'
        )
        for model_id, in_stock, brand_name in prod_qs:
            stock.setdefault(model_id, False)
            stock[model_id] = stock[model_id] or in_stock
            if brand_name:
                brands.setdefault(model_id, set()).add(brand_name)

        used = set()
        for m in qs.iterator(chunk_size=500):
            if m.pk not in stock:  # нет ни одного показываемого товара
                continue
            if self.kind == FEED_MODELS_WORK:
                pictures = self.subcategory_photos(m.sub_category)
            else:
                pictures = self.model_gallery_urls(m)
            model_brands = brands.get(m.pk, ())
            ok = self._add_offer(
                offers,
                offer_id=f'm{m.pk}',
                available=stock[m.pk],
                url=self.abs_path(m.get_absolute_url()),
                price=m.price,
                category_id=m.sub_category_id + SUBCATEGORY_ID_OFFSET,
                pictures=pictures,
                name=m.name,
                vendor=next(iter(model_brands)) if len(model_brands) == 1 else None,
                description=plain_text(m.description),
            )
            if ok:
                used.add(m.sub_category_id)
        return used


def build_feed(kind, base_url=None):
    return FeedBuilder(kind, base_url).build()
