from django.db import models


class Producto(models.Model):
    sku = models.CharField(max_length=40, unique=True)
    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=60, default="General")
    stock_actual = models.PositiveIntegerField(default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.sku} - {self.nombre}"


class RegistroDemanda(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="registros_demanda",
    )
    dia = models.PositiveIntegerField(help_text="Día o índice de tiempo (ej. 1, 2, 3...)")
    unidades_vendidas = models.FloatField(help_text="Unidades demandadas/vendidas en el periodo")

    class Meta:
        ordering = ["dia"]
        unique_together = ("producto", "dia")

    def __str__(self):
        return f"{self.producto.nombre} · Día {self.dia}: {self.unidades_vendidas} u."