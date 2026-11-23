from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer
from .calculo import calcular_integral_general, calcular_integral_producto

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


@api_view(["GET"])
def calculo_inventario(request):
    try:
        dias = int(request.query_params.get("dias", 7))
    except (TypeError, ValueError):
        dias = 7

    producto_id = request.query_params.get("producto_id")
    if producto_id:
        producto = Producto.objects.prefetch_related("registros_demanda").filter(id=producto_id).first()
        if not producto:
            return Response({"error": "Producto no encontrado"}, status=404)
        return Response(calcular_integral_producto(producto, horizonte_dias=dias))

    return Response(calcular_integral_general(horizonte_dias=dias))