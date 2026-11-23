from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "message": "Django + DRF listo para Smart POS"})

@api_view(["GET"])
def resumen_inicial(request):
    return Response({
        "status": "conectado",
        "proyecto": "Control Operativo Smart",
        "productos_ejemplo": [
            {"id": 1, "sku": "BEB-001", "nombre": "Agua embotellada 600ml", "stock": 24, "precio": 2500},
            {"id": 2, "sku": "ABA-002", "nombre": "Café molido 500g", "stock": 6, "precio": 18500},
        ],
    })



@api_view(["GET"])
def resumen_inicial(request):
    productos = Producto.objects.all()
    return Response({
        "status": "conectado",
        "proyecto": "Control Operativo Smart",
        "total_productos": productos.count(),
        "productos_ejemplo": [
            {
                "id": p.id,
                "sku": p.sku,
                "nombre": p.nombre,
                "stock": p.stock_actual,
                "precio": float(p.precio_venta),
            }
            for p in productos[:5]
        ],
    })


@api_view(["GET"])
def listar_productos(request):
    productos = Producto.objects.prefetch_related("registros_demanda").all()
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)