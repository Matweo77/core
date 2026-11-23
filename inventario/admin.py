from django.contrib import admin
from .models import Producto, RegistroDemanda


class RegistroDemandaInline(admin.TabularInline):
    model = RegistroDemanda
    extra = 7  # Te muestra 7 filas listas para llenar días 1..7 de golpe


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("sku", "nombre", "categoria", "stock_actual", "precio_venta", "costo_unitario")
    search_fields = ("sku", "nombre", "categoria")
    inlines = [RegistroDemandaInline]


@admin.register(RegistroDemanda)
class RegistroDemandaAdmin(admin.ModelAdmin):
    list_display = ("producto", "dia", "unidades_vendidas")
    list_filter = ("producto",)    