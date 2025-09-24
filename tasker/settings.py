# Pridajte do INSTALLED_APPS ak ešte nie je:
INSTALLED_APPS = [
    # ... ostatné apps
    'django.contrib.messages',  # Pre notifikácie
    'tasks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

# Middleware pre správy
MIDDLEWARE = [
    # ... ostatné middleware
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Nastavenia pre správy
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}