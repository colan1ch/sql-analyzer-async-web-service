from django.urls import path
from . import views

urlpatterns = [
    path('calculate/', views.calculate, name='calculate'),
    path('health/', views.health_check, name='health'),
]
