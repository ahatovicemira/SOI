from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='soi_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='soi_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('group/<code>', views.group, name='group'),
    path('group/<code>/<task_id>/tasks', views.task, name = 'tasks'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('delete/<group_id>', views.delete_group, name='delete_group'),
    path('update/<group_id>', views.update_group, name='update_group'),
    path('delete-task/<task_id>', views.delete_task, name='delete_task'),
    path('update-test-case/<test_case_id>', views.update_test_case, name='update_test_case'),
    path('group/<task_id>/tasks/input_output', views.input_output, name = 'input_output'),
    path('group/tasks/<fun_name>/<task_id>', views.validate_solution, name='validate_solution'),
    path('report/<user_id>/<group_id>/', views.generate_report_user, name='generate_report_user'),
    path('report/<task_id>/', views.generate_report_task, name='generate_report_task')
   
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


