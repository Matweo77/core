from django.core.management.base import BaseCommand
from inventario.models import Producto, RegistroDemanda


CATALOGO_SIMULADO = [
    {
        "sku": "BEB-001",
        "nombre": "Agua embotellada 600ml",
        "categoria": "Bebidas",
        "stock_actual": 24,
        "costo_unitario": 1200,
        "precio_venta": 2500,
        "demandas": [3, 4, 3, 5, 4, 4, 5],
    },
    {
        "sku": "ABA-002",
        "nombre": "Café molido 500g",
        "categoria": "Abarrotes",
        "stock_actual": 6,
        "costo_unitario": 12000,
        "precio_venta": 18500,
        "demandas": [1, 2, 1, 2, 1, 2, 1],
    },
    {
        "sku": "LAC-003",
        "nombre": "Leche entera 1L",
        "categoria": "Lácteos",
        "stock_actual": 10,
        "costo_unitario": 3100,
        "precio_venta": 4800,
        "demandas": [2, 2, 3, 2, 2, 3, 2],
    },
    {
        "sku": "ABA-004",
        "nombre": "Arroz blanco premium 1kg",
        "categoria": "Abarrotes",
        "stock_actual": 4,
        "costo_unitario": 2400,
        "precio_venta": 3900,
        "demandas": [2, 2, 3, 3, 2, 3, 4],
    },
    {
        "sku": "BEB-005",
        "nombre": "Jugo de naranja natural 1L",
        "categoria": "Bebidas",
        "stock_actual": 15,
        "costo_unitario": 3600,
        "precio_venta": 6200,
        "demandas": [2, 2, 2, 3, 2, 2, 3],
    },
    {
        "sku": "LIM-006",
        "nombre": "Detergente líquido multiusos 1L",
        "categoria": "Limpieza",
        "stock_actual": 28,
        "costo_unitario": 6500,
        "precio_venta": 11200,
        "demandas": [1, 1, 2, 1, 1, 2, 1],
    },
    {
        "sku": "ABA-007",
        "nombre": "Aceite vegetal girasol 900ml",
        "categoria": "Abarrotes",
        "stock_actual": 0,
        "costo_unitario": 7800,
        "precio_venta": 12500,
        "demandas": [2, 3, 2, 3, 4, 3, 3],
    },
    {
        "sku": "LAC-008",
        "nombre": "Yogurt griego natural 200g",
        "categoria": "Lácteos",
        "stock_actual": 19,
        "costo_unitario": 2900,
        "precio_venta": 5200,
        "demandas": [2, 3, 2, 2, 3, 3, 2],
    },
]


class Command(BaseCommand):
    help = "Simula y carga un catálogo de productos y registros diarios de demanda en la base de datos."

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0

        for item in CATALOGO_SIMULADO:
            producto, created = Producto.objects.update_or_create(
                sku=item["sku"],
                defaults={
                    "nombre": item["nombre"],
                    "categoria": item["categoria"],
                    "stock_actual": item["stock_actual"],
                    "costo_unitario": item["costo_unitario"],
                    "precio_venta": item["precio_venta"],
                },
            )
            if created:
                creados += 1
            else:
                actualizados += 1

            # Reemplaza registros previos de ese producto para mantener consistencia en pruebas
            producto.registros_demanda.all().delete()
            registros = [
                RegistroDemanda(
                    producto=producto,
                    dia=idx + 1,
                    unidades_vendidas=unidades,
                )
                for idx, unidades in enumerate(item["demandas"])
            ]
            RegistroDemanda.objects.bulk_create(registros)

        self.stdout.write(
            self.style.SUCCESS(
                f"Listo: {creados} productos creados, {actualizados} actualizados, con 7 días de demanda por producto."
            )
        )