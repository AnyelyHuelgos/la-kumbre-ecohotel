# La Kumbre del Huila - codigo de cPanel (copia de desarrollo)

Esta es la base de codigo extraida de cPanel para trabajar de manera independiente del sitio en produccion.

## Estado
- Django, HTML, CSS y JavaScript del sitio publicado.
- No incluye datos de clientes, archivos .env, fotos originales ni videos.
- La biblioteca de fotos optimizadas se encuentra en la rama independiente de GitHub destinada a desarrollo.
- No se ha verificado todavia la ejecucion completa ni los pagos.

## Desarrollo local
1. Instala Python 3.12 y crea un entorno virtual: `python -m venv .venv`.
2. Activa el entorno e instala: `pip install -r requirements.txt`.
3. Copia `.env.example` a `.env` y define una clave aleatoria propia.
4. Crea una base de datos local VACIA: `python manage.py migrate`.
5. Inicia el entorno local: `python manage.py runserver`.

IMPORTANTE: no conectar el desarrollo con la base de datos ni las claves reales de cPanel.
Para enviar cualquier actualizacion al sitio publicado se requieren pruebas y un respaldo independiente.

## Pendientes
La seguridad, reservas, pagos, integridad de base de datos, experiencia de usuario y rendimiento se revisaran por fases.
Consulta `PLAN_DE_TRABAJO.md`.
