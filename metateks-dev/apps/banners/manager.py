from django.db import models
from django.db.models import Q
from django.utils import timezone


class BannerQueryset(models.QuerySet):

    def published(self):
        now = timezone.now()
        return self.filter(
            (Q(end_dt=None) | Q(end_dt__gte=now)),
            start_dt__lte=now,
            is_published=True,
        )

    def not_published(self):
        now = timezone.now()
        return self.exclude(
            (Q(end_dt=None) | Q(end_dt__gte=now)),
            start_dt__lte=now,
            is_published=True,
        )


class BannerManager(models.Manager):
    pass
