"""Reglas de anticipos para reservas y productos de La Kumbre."""
from decimal import Decimal


def calcular_anticipo(total_reservas, total_productos, *, hay_reservas):
    """Calcula el dinero a transferir, sin declarar ningún pago como recibido.

    Con alojamiento: 70 % de cabañas + 100 % de productos.
    Solo productos: 50 % de productos.
    """
    reservas = Decimal(str(total_reservas))
    productos = Decimal(str(total_productos))
    if reservas < 0 or productos < 0:
        raise ValueError("Los totales del carrito no pueden ser negativos")
    anticipo = (reservas * Decimal("0.7") + productos) if hay_reservas else productos * Decimal("0.5")
    return anticipo.quantize(Decimal("1"))
