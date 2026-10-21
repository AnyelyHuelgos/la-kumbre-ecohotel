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

from datetime import date

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Compra, Reserva


class ReservaIntegridadTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="cliente_prueba", password="ClaveSoloDePruebas123!")

    def _crear_reserva(self):
        return Reserva.objects.create(
            usuario=self.usuario,
            cabana="Tabi",
            fecha=date(2027, 2, 12),
            precio=Decimal("400000"),
            telefono="3000000000",
            numero_personas=2,
            estado="Pendiente",
            confirmada=True,
        )

    def test_base_de_datos_rechaza_dos_reservas_misma_fecha(self):
        self._crear_reserva()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._crear_reserva()
        self.assertEqual(Reserva.objects.count(), 1)

    def test_operacion_incompleta_se_revierte(self):
        self._crear_reserva()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Compra.objects.create(
                    usuario=self.usuario,
                    nombre="Cliente de prueba",
                    email="pruebas@example.com",
                    telefono="3000000000",
                    total=Decimal("400000"),
                    metodo_pago="nequi",
                    pagado=False,
                )
                self._crear_reserva()
        self.assertFalse(Compra.objects.exists())
