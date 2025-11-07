from django.db import models
from django.utils.timezone import now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ActiveModel(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, verbose_name='ID')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def activate(self):
        self.is_active = True
        self.is_deleted = False
        self.save()

    def deactivate(self):
        self.is_active = False
        self.is_deleted = True
        self.save()
