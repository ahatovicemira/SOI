from django.contrib import admin
from .models import lkpRole, User, Group, lkpSubject

# Register your models here.
admin.site.register(lkpRole)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(lkpSubject)