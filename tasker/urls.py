from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.task_list, name='home'),   # root -> zoznam úloh
    path('task/', include('tasks.urls')),     # /task/... -> ostatné task routy
]
