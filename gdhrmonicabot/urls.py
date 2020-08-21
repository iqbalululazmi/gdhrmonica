from django.contrib import admin
from django.urls import path
from apps.bot.views import get_updates
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', get_updates),
]
