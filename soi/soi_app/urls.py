from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='soi_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='soi_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('group/<code>', views.group, name='group'),
    path('group/<code>/<task_id>/tasks', views.task, name = 'tasks'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog')
]

