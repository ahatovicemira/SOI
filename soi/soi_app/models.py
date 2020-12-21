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


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.TextField()
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    visible = models.DateTimeField()
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.name


class TaskInputOutput(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    input = models.TextField()
    output = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.task.__str__()


class Results(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )
    score = models.FloatField()
    last_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(default=timezone.now)
    objects = models.Manager()

    def __str__(self):
        return self.task.__str__(), self.user.__str__()
