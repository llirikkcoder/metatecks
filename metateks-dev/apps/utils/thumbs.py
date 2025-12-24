from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from apps.utils.common import absolute as absolute_url


def get_thumb_url(image, key, absolute=True):
    if not image:
        return None
    url = thumbnail_url(image, key)
    if absolute:
        url = absolute_url(url)
    return url
