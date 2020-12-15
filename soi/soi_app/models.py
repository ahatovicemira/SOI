from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class lkpRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(
        lkpRole,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=None
    )
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username


class lkpSubject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.name


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=30,
        null=True
    )
    subject = models.ForeignKey(
        lkpSubject,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=None
    )

    code = models.CharField(max_length=8)
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    users = models.ManyToManyField('User', blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.name
