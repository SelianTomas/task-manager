from django.contrib import admin
from django.urls import path, include
from tasks import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.task_list, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),  # prihlasovanie + odhlasovanie
    path('accounts/login/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('task/', include('tasks.urls')),
]
