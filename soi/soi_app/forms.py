import random
import string
import datetime
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from .models import User, Group, Task



class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', ]


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    random.seed(datetime.datetime.now())
    return ''.join(random.choice(chars) for _ in range(size))


class GroupCreationForm(ModelForm):
    code = forms.CharField(initial=id_generator, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Group
        fields = ['name', 'subject', 'code']


class StudentAddGroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ['code']


class TaskCreationForm(ModelForm):

    visible = forms.SplitDateTimeField(widget=AdminSplitDateTime())
    started_at = forms.SplitDateTimeField(widget=AdminSplitDateTime())
    finished_at = forms.SplitDateTimeField(widget=AdminSplitDateTime())

    class Meta:
        model = Task
        fields = ['name', 'description',
                  'started_at',
                  'finished_at',
                  'visible',
                  'group']
