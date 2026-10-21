"""Pruebas iniciales de los anticipos y de los accesos de seguridad."""
from decimal import Decimal

from django.test import SimpleTestCase
from django.urls import reverse

from .pagos import calcular_anticipo


class CalculoAnticipoTests(SimpleTestCase):
    def test_reserva_y_productos_sumados(self):
        self.assertEqual(
            calcular_anticipo(400000, 100000, hay_reservas=True), Decimal("380000")
        )

    def test_solo_reserva(self):
        self.assertEqual(
            calcular_anticipo(400000, 0, hay_reservas=True), Decimal("280000")
        )

    def test_solo_productos(self):
        self.assertEqual(
            calcular_anticipo(0, 100000, hay_reservas=False), Decimal("50000")
        )

    def test_carrito_vacio(self):
        self.assertEqual(
            calcular_anticipo(0, 0, hay_reservas=False), Decimal("0")
        )

    def test_valores_negativos_rechazados(self):
        with self.assertRaises(ValueError):
            calcular_anticipo(-1, 5000, hay_reservas=True)


class AccesoTests(SimpleTestCase):
    def test_url_de_depuracion_no_publicada(self):
        response = self.client.get("/debug-productos/")
        self.assertEqual(response.status_code, 404)

    def test_metodos_de_pago_exigen_sesion(self):
        response = self.client.get(reverse("metodos_pago"))
        self.assertEqual(response.status_code, 302)
