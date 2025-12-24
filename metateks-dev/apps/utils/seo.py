from django.utils.safestring import mark_safe

from apps.utils.common import get_current_city


SEO_FIELDS = ['title', 'h1', 'meta_desc', 'meta_keyw']

SEO_INSTRUCTION = mark_safe("""
    Можно использовать следующие теги:
    <ul>
      <li><strong>%city%</strong> – название города ("Москва")</li>
      <li><strong>%city_loct%</strong> – название города в предл. падеже ("Москве")</li>
      <li><strong>%region%</strong> – название региона ("Московская область")</li>
      <li><strong>%region_loct%</strong> – название региона в предл.падеже ("Московской области")</li>
    </ul>
""")


def seo_replace(s, city=None):
    city = city or get_current_city()
    return s.replace('%city%', city.get_name())\
            .replace('%city_loct%', city.get_name_loct())\
            .replace('%region%', city.get_region_name())\
            .replace('%region_loct%', city.get_region_name_loct())
