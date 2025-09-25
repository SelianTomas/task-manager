from django.contrib import admin
from django.urls import path, include
from tasks import views
from django.conf import settings
from django.conf.urls.static import static
from tasks import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('tasks/', include('tasks.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
]


# Obsluha static súborov v development móde
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])