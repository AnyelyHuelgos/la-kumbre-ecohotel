"""Reglas de anticipo para reservas y productos de La Kumbre.

Una reserva con productos requiere 70% de las reservas y 100% de los
productos. Un pedido sin reservas requiere 50% de los productos.
El resultado se redondea al peso colombiano como las vistas anteriores.
"""
from decimal import Decimal


def calcular_anticipo(total_reservas, total_productos):
    reservas = Decimal(str(total_reservas))
    productos = Decimal(str(total_productos))
    if reservas < 0 or productos < 0:
        raise ValueError("Los totales del carrito no pueden ser negativos")
    if reservas > 0:
        pago_inicial = reservas * Decimal("0.7") + productos
    else:
        pago_inicial = productos * Decimal("0.5")
    return pago_inicial.quantize(Decimal("1"))
