from rest_framework import serializers
from .models import Producto, RegistroDemanda


class RegistroDemandaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroDemanda
        fields = ["id", "dia", "unidades_vendidas"]


class ProductoSerializer(serializers.ModelSerializer):
    registros_demanda = RegistroDemandaSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "sku",
            "nombre",
            "categoria",
            "stock_actual",
            "precio_venta",
            "costo_unitario",
            "registros_demanda",
        ]