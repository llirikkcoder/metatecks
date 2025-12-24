from django.db import models
from django.db.models import Q
from django.utils import timezone


class IsPublishedQueryset(models.QuerySet):

    def published(self):
        now = timezone.now()
        return self.filter(
            published_at__lte=now,
            is_published=True,
        )

    def not_published(self):
        now = timezone.now()
        return self.exclude(
            published_at__lte=now,
            is_published=True,
        )


class IsPublishedManager(models.Manager):
    pass
