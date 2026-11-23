from django.urls import path
from . import views

urlpatterns = [
    path("resumen/", views.resumen_inicial),
    path("productos/", views.listar_productos),
]