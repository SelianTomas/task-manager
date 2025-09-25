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


# pre obrázky (avatar)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
