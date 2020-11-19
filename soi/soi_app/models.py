from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class lkpRole(models.Model):
    name = models.CharField(max_length=10)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name