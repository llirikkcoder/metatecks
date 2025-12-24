from django.db import models
from django.db.models import Q
from django.utils import timezone

from crequest.middleware import CrequestMiddleware


class PromotionQueryset(models.QuerySet):

    def active(self):
        now = timezone.now().date()
        return self.filter(
            (Q(end_dt=None) | Q(end_dt__gte=now)),
            (Q(model_id__gt=0) | Q(product_id__gt=0)),
            start_dt__lte=now,
            is_active=True,
        )

    def not_active(self):
        now = timezone.now()
        return self.exclude(
            (Q(end_dt=None) | Q(end_dt__gte=now)),
            (Q(model_id__gt=0) | Q(product_id__gt=0)),
            start_dt__lte=now,
            is_active=True,
        )


class PromotionManager(models.Manager):
    pass


from django.db.models import Q

