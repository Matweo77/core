import numpy as np
from .models import Producto


def _integrar_trapecio(t: np.ndarray, y: np.ndarray) -> float:
    """Integra numéricamente y(t) respecto a t usando la regla del trapecio."""
    if len(t) < 2:
        return float(np.sum(y)) if len(y) else 0.0
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, t))
    return float(np.trapz(y, t))


def calcular_integral_producto(producto: Producto, horizonte_dias: int = 7) -> dict:
    """
    Calcula métricas de cálculo integral sobre la serie de demanda de un producto
    y estima el tiempo de agotamiento de su stock actual S0.
    """
    horizonte = max(1, int(horizonte_dias))
    stock_0 = float(producto.stock_actual or 0)
    registros = list(producto.registros_demanda.order_by("dia").values("dia", "unidades_vendidas"))

    if not registros:
        return {
            "producto_id": producto.id,
            "sku": producto.sku,
            "nombre": producto.nombre,
            "categoria": producto.categoria,
            "stock_actual": stock_0,
            "horizonte_dias": horizonte,
            "demanda_acumulada_historica": 0.0,
            "tasa_promedio_diaria": 0.0,
            "demanda_proyectada_horizonte": 0.0,
            "dias_estimados_agotamiento": None,
            "estado_agotamiento": "Sin datos de demanda",
            "formula_resumen": "Sin registros históricos r(t)",
            "curva": [],
        }

    t_hist = np.array([float(r["dia"]) for r in registros], dtype=float)
    r_hist = np.array([float(r["unidades_vendidas"]) for r in registros], dtype=float)

    # Integral definida histórica: ∫ r(t) dt sobre los días registrados
    demanda_historica = _integrar_trapecio(t_hist, r_hist)
    span_dias = max(float(t_hist[-1] - t_hist[0]), 1.0)
    tasa_promedio = max(demanda_historica / span_dias, 0.0)

    # Curva continua r(t) en paso fino (dt = 0.25 días) para integrar con alta resolución
    # Combinamos tendencia suave (grado 1 acotada) con tasa promedio para estabilidad numérica
    if len(t_hist) >= 3 and tasa_promedio > 0:
        pendiente, _ = np.polyfit(t_hist, r_hist, 1)
        # Limitamos la pendiente para evitar explosiones en horizontes largos
        pendiente_acotada = float(np.clip(pendiente, -0.5 * tasa_promedio, 0.5 * tasa_promedio))
    else:
        pendiente_acotada = 0.0

    t_fin = max(float(t_hist[-1]), float(horizonte))
    t_grid = np.arange(0.0, t_fin + 0.25, 0.25)

    # r(t) >= 0 centrada respecto al último día histórico
    t_ref = float(t_hist[-1])
    r_curva = np.maximum(0.0, tasa_promedio + pendiente_acotada * (t_grid - t_ref))

    # Demanda acumulada proyectada en el horizonte [0, horizonte]: ∫_0^T r(t) dt
    mask_horizonte = t_grid <= float(horizonte)
    demanda_horizonte = _integrar_trapecio(t_grid[mask_horizonte], r_curva[mask_horizonte])

    # Tiempo estimado de agotamiento t*: ∫_0^{t*} r(t) dt = S0
    if stock_0 <= 0:
        dias_agotamiento = 0.0
        estado = "Agotado"
    elif tasa_promedio <= 0 and np.all(r_curva <= 0):
        dias_agotamiento = None
        estado = "Sin rotación (demanda 0)"
    else:
        acumulada_grid = np.zeros_like(t_grid)
        for i in range(1, len(t_grid)):
            dt = t_grid[i] - t_grid[i - 1]
            acumulada_grid[i] = acumulada_grid[i - 1] + 0.5 * (r_curva[i - 1] + r_curva[i]) * dt

        if acumulada_grid[-1] < stock_0:
            # Extender grilla si el stock tarda más que t_fin en agotarse
            extra_t = np.arange(t_grid[-1] + 0.25, max(t_fin * 4, 30.0) + 0.25, 0.25)
            extra_r = np.maximum(0.0, tasa_promedio + pendiente_acotada * (extra_t - t_ref))
            if np.all(extra_r <= 0):
                dias_agotamiento = None
                estado = "Sin rotación suficiente"
            else:
                prev_t, prev_r, prev_ac = t_grid[-1], r_curva[-1], acumulada_grid[-1]
                dias_agotamiento = None
                for ti, ri in zip(extra_t, extra_r):
                    dt = ti - prev_t
                    sig_ac = prev_ac + 0.5 * (prev_r + ri) * dt
                    if sig_ac >= stock_0:
                        frac = (stock_0 - prev_ac) / max(sig_ac - prev_ac, 1e-9)
                        dias_agotamiento = round(float(prev_t + frac * dt), 2)
                        break
                    prev_t, prev_r, prev_ac = ti, ri, sig_ac
                estado = "Riesgo próximo" if (dias_agotamiento is not None and dias_agotamiento <= 7) else "Estable"
        else:
            idx = int(np.searchsorted(acumulada_grid, stock_0, side="left"))
            if idx == 0:
                dias_agotamiento = 0.0
            else:
                t0, t1 = t_grid[idx - 1], t_grid[idx]
                a0, a1 = acumulada_grid[idx - 1], acumulada_grid[idx]
                frac = (stock_0 - a0) / max(a1 - a0, 1e-9)
                dias_agotamiento = round(float(t0 + frac * (t1 - t0)), 2)
            estado = "Crítico (<= 3 días)" if dias_agotamiento <= 3 else (
                "Riesgo próximo (<= 7 días)" if dias_agotamiento <= 7 else "Estable"
            )

    # Puntos muestreados para graficar en frontend
    puntos_curva = [
        {
            "t": round(float(t_grid[i]), 2),
            "demanda_tasa": round(float(r_curva[i]), 2),
        }
        for i in range(0, len(t_grid), 4)  # cada 1.0 día
    ]

    return {
        "producto_id": producto.id,
        "sku": producto.sku,
        "nombre": producto.nombre,
        "categoria": producto.categoria,
        "stock_actual": round(stock_0, 2),
        "horizonte_dias": horizonte,
        "demanda_acumulada_historica": round(demanda_historica, 2),
        "tasa_promedio_diaria": round(tasa_promedio, 2),
        "demanda_proyectada_horizonte": round(demanda_horizonte, 2),
        "dias_estimados_agotamiento": dias_agotamiento,
        "estado_agotamiento": estado,
        "formula_resumen": f"∫₀^{horizonte} r(t) dt = {round(demanda_horizonte, 2)} uds.",
        "curva": puntos_curva,
    }


def calcular_integral_general(horizonte_dias: int = 7) -> dict:
    """Calcula el análisis integral para todos los productos y un resumen global."""
    productos = Producto.objects.prefetch_related("registros_demanda").all()
    resultados = [calcular_integral_producto(p, horizonte_dias=horizonte_dias) for p in productos]

    total_demanda_horizonte = round(
        sum(item["demanda_proyectada_horizonte"] for item in resultados), 2
    )
    total_demanda_historica = round(
        sum(item["demanda_acumulada_historica"] for item in resultados), 2
    )
    con_agotamiento = [
        item["dias_estimados_agotamiento"]
        for item in resultados
        if item["dias_estimados_agotamiento"] is not None
    ]
    menor_agotamiento = min(con_agotamiento) if con_agotamiento else None

    return {
        "horizonte_dias": max(1, int(horizonte_dias)),
        "resumen": {
            "total_productos": len(resultados),
            "demanda_acumulada_historica": total_demanda_historica,
            "demanda_proyectada_horizonte": total_demanda_horizonte,
            "menor_dias_agotamiento": menor_agotamiento,
        },
        "productos": resultados,
    }