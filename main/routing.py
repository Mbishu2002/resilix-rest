from django.urls import path
from . import consumers

urlpatterns = [
    path('ws/alerts/', consumers.AlertConsumer.as_asgi()),  
]
