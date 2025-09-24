from django.contrib import admin
from django.urls import path, include
from tasks import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.task_list, name='home'),

    # Allauth (registrácia, login, logout, reset hesla, Google SSO)
    path('accounts/', include('allauth.urls')),

    #  appky
    path('task/', include('tasks.urls')),
]

# pre obrázky (avatar)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
