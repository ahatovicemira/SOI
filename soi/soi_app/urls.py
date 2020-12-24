from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    #path('student', views.index, name = 'home-student'),
    path('login/', auth_views.LoginView.as_view(template_name='soi_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='soi_app/logout.html'), name='logout'),
    #path('login/', auth_views.LoginView.as_view(template_name='soi_app/login.html'), name = 'login'),
    #path('logout/', auth_views.LogoutView.as_view(template_name='soi_app/logout.html'), name = 'logout'),
    path('register/', views.register, name = 'register'),
    path('group/<code>', views.group, name='group'),
    path('delete/<group_id>', views.delete_group, name='delete_group'),
    path('update/<group_id>', views.update_group, name='update_group'),
]

