from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Sugerencia
from .forms import SugerenciaForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Usuario
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse 
from .models import Reserva, Cabana, Producto
from datetime import date
from django.http import JsonResponse
import json
from datetime import datetime
from django.core.mail import send_mail
from .forms import ReservaForm
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, CarritoProducto
from django.db.models import Sum, F
from .forms import MetodoPagoForm
from .models import Compra, DetalleCompra
from .forms import CompraForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# Agrega esta vista temporal para debug
def debug_productos(request):
    """Vista temporal para debuggear productos y sus precios"""
    productos = Producto.objects.all()
    
    debug_info = []
    for producto in productos:
        info = {
            'nombre': producto.nombre,
            'tipo': producto.tipo_producto,
            'precio_base': producto.precio,
            'precio_copa': producto.precio_copa,
            'precio_jarra': producto.precio_jarra,
        }
        
        if producto.tipo_producto == 'bebida':
            info['precio_copa_calculado'] = producto.get_precio_por_presentacion('copa')
            info['precio_jarra_calculado'] = producto.get_precio_por_presentacion('jarra')
        else:
            info['precio_calculado'] = producto.get_precio_por_presentacion()
            
        debug_info.append(info)
    
    return JsonResponse({'productos': debug_info})



def inicio(request):
    usuario_id = request.session.get("usuario_id")
    correo = request.session.get("correo")

    return render(request, "inicio.html", {"correo": correo})

def quienes_somos(request):
    return render(request, 'quienes_somos.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def mapa(request):
    return render(request, 'mapa.html')

def galeria(request):
    return render(request, 'galeria.html')

def restaurante(request):
    return render(request, 'restaurante.html')

def atracciones(request):
    return render(request, 'atracciones.html')
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Producto, CarritoProducto
from itertools import groupby
from operator import attrgetter
import json

def lista_productos(request):
    # Obtener solo productos originales (no los del carrito)
    productos = Producto.objects.filter(en_carrito=False)
    
    # FORZAR el orden: COMIDA PRIMERO, BEBIDA DESPUÉS
    productos_agrupados = []
    
    # 1. PRIMERO LAS COMIDAS
    productos_comida = productos.filter(tipo_producto='comida').order_by('nombre')
    if productos_comida.exists():
        productos_agrupados.append(('comida', list(productos_comida)))
    
    # 2. DESPUÉS LAS BEBIDAS  
    productos_bebida = productos.filter(tipo_producto='bebida').order_by('nombre')
    if productos_bebida.exists():
        productos_agrupados.append(('bebida', list(productos_bebida)))
    
    # Debug para ver qué pasa
    print("=== ORDEN FINAL ===")
    for tipo, lista in productos_agrupados:
        print(f"{tipo.upper()}: {len(lista)} productos")
    
    
    context = {
        'productos_agrupados': productos_agrupados,
    }
    return render(request, 'productos.html', context)
    

@login_required
@require_POST
def agregar_producto_carrito(request, producto_id):
    try:
        producto_original = get_object_or_404(Producto, id=producto_id)
        
        # Obtener datos del request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            cantidad = int(data.get('cantidad', 1))
            presentacion = data.get('presentacion', None)
        else:
            cantidad = int(request.POST.get('cantidad', 1))
            presentacion = request.POST.get('presentacion', None)
        
        # Para bebidas, validar presentacion
        if producto_original.tipo_producto == 'bebida':
            if not presentacion:
                presentacion = 'copa'  # Por defecto
        else:
            presentacion = None
        
        # Calcular precio unitario correcto ANTES de crear/actualizar
        precio_unitario = producto_original.get_precio_por_presentacion(presentacion)
        
        # DEBUG: Imprimir valores para verificar
        print(f"Producto: {producto_original.nombre}")
        print(f"Tipo: {producto_original.tipo_producto}")
        print(f"Presentacion: {presentacion}")
        print(f"Precio copa: {producto_original.precio_copa}")
        print(f"Precio jarra: {producto_original.precio_jarra}")
        print(f"Precio base: {producto_original.precio}")
        print(f"Precio calculado: {precio_unitario}")
        
        # Verificar si ya existe
        carrito_existente = CarritoProducto.objects.filter(
            usuario=request.user,
            producto=producto_original,
            presentacion=presentacion
        ).first()
        
        if carrito_existente:
            carrito_existente.cantidad += cantidad
            # Actualizar precio por si cambió
            carrito_existente.precio_unitario = precio_unitario
            carrito_existente.save()
        else:
            # Crear con precio unitario ya calculado
            CarritoProducto.objects.create(
                usuario=request.user,
                producto=producto_original,
                cantidad=cantidad,
                presentacion=presentacion,
                precio_unitario=precio_unitario
            )
        
        cart_count = CarritoProducto.objects.filter(usuario=request.user).count()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Producto agregado exitosamente',
            'cart_count': cart_count,
            'precio_final': float(precio_unitario)
        })
        
    except Exception as e:
        print(f"Error en agregar_producto_carrito: {str(e)}")
        return JsonResponse({
            'success': False,
            'mensaje': f'Error: {str(e)}'
        }, status=400)
        

def restricciones(request):
    return render(request, 'restricciones.html')

def cabanas(request):
    return render(request, 'cabanas.html')

def cabanatabi(request):
    return render(request, 'cabanatabi.html')

def cabanageisha(request):
    return render(request, 'cabanageisha.html')

def cabanacafetal(request):
    return render(request, 'cabanacafetal.html')

def cabanabourbon(request):
    return render(request, 'cabanabourbon.html')

def cabanawush(request):
    return render(request, 'cabanawush.html')

def perfil(request):
    return render(request, 'perfil.html')

def spots(request):
    return render(request, 'spots.html')

def columpio(request):
    return render(request, 'columpio.html')
    
    
    
   # views.py
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def sugerencias(request):
    if request.method == 'POST':
        form = SugerenciaForm(request.POST)
        if form.is_valid():
            sugerencia = form.save()
            
            # Renderizar la plantilla HTML para el correo
            html_message = render_to_string('email_template.html', {
                'sugerencia': sugerencia
            })
            plain_message = strip_tags(html_message)
            
            # Correo para Anyely (administrador) con plantilla HTML
            send_mail(
                'Hola Anyely! Tienes una nueva Sugerencia 📝',
                plain_message,
                'lakumbredelhuila01@gmail.com', 
                ['lakumbredelhuila01@gmail.com'],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, "Tu sugerencia ha sido enviada con éxito.")
            return redirect('sugerencias') 
    else:
        form = SugerenciaForm()
    return render(request, 'sugerencias.html', {'form': form})
    
    
def confirmacion_compra_usuario(request):
    return render(request, 'confirmacion_compra_usuario.html')

def nueva_compra_admin(request):
    return render(request, 'nueva_compra_admin.html')
    
def email_template(request):
    return render(request, 'email_template.html')

@login_required
def historial(request):
    # Obtener todas las reservas del usuario (tanto confirmadas como pendientes)
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha')
    
    # Obtener todas las compras del usuario
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'historial.html', {
        'reservas': reservas,
        'compras': compras
    })
    

def manual(request):
    return render(request, 'manual.html')


def registro(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        telefono = request.POST['telefono']
        # Validaciones
        error = None
        if password != confirm_password:
            error = 'Las contrasenas no coinciden'
        elif User.objects.filter(username=username).exists():
            error = 'El nombre de usuario ya esta en uso'
        if error:
            messages.error(request, error)
            # En lugar de redirigir, renderizamos la misma plantilla con los datos ingresados
            return render(request, 'iniciar_sesion.html', {
                'register_mode': True,
                'datos_previos': {
                    'username': username,
                    'telefono': telefono
                }
            })
        # Si no hay errores, crear el usuario
        # Creamos un correo ficticio basado en el nombre de usuario para cumplir con el modelo User
        email = f"{username}@lakumbre.com"
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Crear el perfil de usuario con el tel��fono
        usuario_perfil = Usuario(usuario=user, telefono=telefono)
        usuario_perfil.save()
        
        messages.success(request, "Registro Exitoso! Ahora inicia sesion.")
        return redirect('iniciar_sesion')
    return render(request, 'iniciar_sesion.html', {'register_mode': True})


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout

def iniciar_sesion(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Hola {user.username} Haz iniciado sesion en La Kumbre!")
                return redirect('inicio')
            else:
                messages.error(request, "Usuario o contrasena incorrectos")
        else:
            messages.error(request, "Usuario o contrasena incorrectos")
    return render(request, 'iniciar_sesion.html', {'register_mode': False})
    


def logout_perfil(request):
    if request.user.is_authenticated:
        nombre_usuario = request.user.username  
        messages.success(request, f"Adios {nombre_usuario}. Vuelve pronto!")  
    
    logout(request)
    request.session.flush()  # Solo agrega esta línea
    
    return redirect("inicio")
    
  

@login_required
def hacer_reserva(request):
    if request.method == "POST":
        cabana_id = request.POST.get("cabana_id")
        fecha_str = request.POST.get("fecha")
        telefono = request.POST.get("telefono")
        tiene_adicionales = request.POST.get("tiene_personas_adicionales", "no")
        personas_adicionales = int(request.POST.get("personas_adicionales", 0)) if tiene_adicionales == "si" else 0
        
        # Obtener el precio total calculado en el frontend
        precio_total_str = request.POST.get("precio_total")
        precio_adicional_str = request.POST.get("precio_personas_adicionales")
   
        try:
            cabana = get_object_or_404(Cabana, id=cabana_id)
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            if fecha < datetime.now().date():
                messages.error(request, "No se puede reservar en fechas pasadas.")
                return redirect('cabanas')
            
            precios = PrecioCabana.objects.get(cabana=cabana)
            es_festivo = Festivo.objects.filter(fecha=fecha).exists()
            # Corregido: dia 4 es viernes (0=Lunes, ..., 4=Viernes, 5=Sabado, 6=Domingo)
            es_finde = fecha.weekday() in [4, 5]  # Incluir viernes como fin de semana
            
            # Determinar precio base segun el dia
            if es_festivo:
                precio_base = float(precios.precio_festivo)
                tipo_dia = 'festivo'
            elif es_finde:
                precio_base = float(precios.precio_fin_semana)
                tipo_dia = 'fin_semana'
            else:
                precio_base = float(precios.precio_entre_semana)
                tipo_dia = 'entre_semana'
            
            # CORRECCION: Calcular precio por persona adicional
            if precios.es_cabana_especial:
                # Para cabana Cafetal: precios diferenciados
                if tipo_dia == 'entre_semana':
                    precio_extra = float(precios.precio_persona_adicional_entre_semana)
                else:
                    precio_extra = float(precios.precio_persona_adicional_finde_festivo)
            else:
                # Para todas las demas cabanas: 80,000 todos los dias
                precio_extra = 80000.00
            
            # Calcular precio adicional y total
            precio_adicional = personas_adicionales * precio_extra
            precio_total = precio_base + precio_adicional
            
            # Guardar datos de reserva
            reserva_data = {
                'cabana_id': cabana.id,
                'cabana': cabana.nombre,
                'fecha': fecha_str,
                'telefono': telefono,
                'numero_personas': 2 + personas_adicionales,  # Total de personas
                'personas_adicionales': personas_adicionales,
                'precio_personas_adicionales': precio_adicional,
                'precio': precio_total,
                'tipo_dia': tipo_dia,
                'es_finde_o_festivo': es_finde or es_festivo
            }
            
            # Guardar en la sesion
            reservas = request.session.get('reservas_carrito', [])
            reservas.append(reserva_data)
            request.session['reservas_carrito'] = reservas
            request.session.modified = True
            
            messages.success(request, "Reserva anadida al carrito puedes continuar comprando.")
            return redirect('productos')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('cabanas')
    else:
        cabana_id = request.GET.get("cabana_id")
        context = {}
        if cabana_id:
            cabana = get_object_or_404(Cabana, id=cabana_id)
            context["cabana"] = cabana
        return render(request, "reservas.html", context)
        
        
@login_required
def resumen_compra(request):
    reservas_sesion = request.session.get('reservas_carrito', [])
    
    # Depuracion: Imprimir detalles de las reservas
    for idx, r in enumerate(reservas_sesion):
        print(f"Reserva {idx}:")
        print(f"  Fecha: {r['fecha']}")
        print(f"  Personas adicionales: {r['personas_adicionales']}")
        print(f"  Precio personas adicionales: {r['precio_personas_adicionales']}")
        print(f"  Precio total: {r['precio']}")
    
    productos = CarritoProducto.objects.filter(usuario=request.user)
    # Convertir objetos reserva de sesion en objetos simulados
    reservas = []
    for idx, r in enumerate(reservas_sesion):
        reservas.append(type('Reserva', (object,), {
            'id': idx,
            **r
        })())
    return render(request, 'resumen_compra.html', {
        'reservas': reservas,
        'productos': productos,
    })
    
    
    
@login_required
def eliminar_reserva(request, reserva_id):
    reservas_sesion = request.session.get('reservas_carrito', [])

    if 0 <= reserva_id < len(reservas_sesion):
        del reservas_sesion[reserva_id]
        request.session['reservas_carrito'] = reservas_sesion
        request.session.modified = True
        messages.success(request, "Reserva eliminada correctamente")
        return redirect('resumen_compra')
    else:
        return JsonResponse({'error': 'Indice de reserva no valido.'}, status=400)


def obtener_fechas_ocupadas(request, cabana_id):
    # Buscar todas las reservas para esta cabana
    cabana = get_object_or_404(Cabana, id=cabana_id)
    reservas = Reserva.objects.filter(cabana=cabana.nombre).values_list('fecha', flat=True)
    fechas_ocupadas = [fecha.strftime("%Y-%m-%d") for fecha in reservas]
    return JsonResponse({'fechas_ocupadas': fechas_ocupadas})

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        user = request.user
        nombre_usuario = user.username
        user.delete()
        messages.success(request, f"Adios, {nombre_usuario}. !Tu cuenta ha sido eliminada con exito!")
        return redirect('home')  # Redirige a la p��gina de inicio despu��s de eliminar la cuenta
    return render(request, 'eliminar_cuenta.html')

from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required


@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Importante para mantener la sesi��n
            messages.success(request, '!Tu contrasena ha sido actualizada con exito!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores a continuacion.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'cambiar_contrasena.html', {'form': form})



def restablecer(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            enlace = request.build_absolute_uri(f"/contrasena/{uid}/{token}/")
            send_mail(
                "Restablecimiento de Contrasena",
                f"Haz clic en el siguiente enlace para restablecer tu contrasena:\n\n{enlace}",
                "anyelyho@gmail.com",
                [email],
                fail_silently=False,
            )
            messages.success(request, "Se ha enviado un enlace a tu correo para restablecer tu contrasena.")
            return redirect("inicio")
        else:
            messages.error(request, "No se encontro un usuario con ese correo electronico.")
            return redirect("restablecer")
        
    return render(request, "restablecer.html")


def contrasena(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            nueva_contrasena = request.POST["password"]
            user.set_password(nueva_contrasena)
            user.save()
            return redirect("password_changed")
        return render(request, "contrasena.html")
    return redirect("iniciar_sesion")


def password_changed(request):
    return render(request, "password_changed.html")


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import CarritoProducto

@login_required
def eliminar_producto(request, producto_id):
    if request.method == "POST":
        try:
            producto = get_object_or_404(CarritoProducto, id=producto_id, usuario=request.user)
            producto.delete()
            
            # Calcular el total de productos en el carrito
            total = CarritoProducto.objects.filter(usuario=request.user).aggregate(
                total=Sum('cantidad')
            )['total'] or 0

            return JsonResponse({'success': True, 'cart_count': total})

        except Exception as e:
            return JsonResponse({'success': False, 'mensaje': f'Error al eliminar: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'mensaje': 'Metodo invalido.'}, status=400)

    
@login_required
def metodo_pago(request):
    from decimal import Decimal
    metodo = request.GET.get('metodo', '')
    
    productos = CarritoProducto.objects.filter(usuario=request.user)
    reservas_sesion = request.session.get('reservas_carrito', [])
    reservas = []
    total_reservas = Decimal('0')
    for idx, r in enumerate(reservas_sesion):
        # Asegurarse de que el precio sea Decimal
        precio_reserva = Decimal(str(r['precio']))
        total_reservas += precio_reserva
        # Guardar el precio ya convertido
        r_copy = r.copy()
        r_copy['precio'] = precio_reserva
        reservas.append(type('Reserva', (object,), {
            'id': idx,
            **r_copy
        })())
    
    # REEMPLAZAR este bloque en la función metodo_pago:
    total_productos = Decimal('0')
    for item in productos:
        # Usar el precio_unitario que ya está calculado en el modelo
        precio_total = item.precio_unitario * item.cantidad
        total_productos += precio_total
    
    # Asegurarse de que sea Decimal
    total_productos = Decimal(str(total_productos))
    total_carrito = total_productos + total_reservas
   
    
    # CODIGO CORREGIDO: Calcular el total a pagar segun las reglas
    if reservas:
        # 70% del valor de reservas + 100% del valor de productos
        total_a_pagar = (total_reservas * Decimal('0.7'))  
    else:
        # 50% del valor de productos
        total_a_pagar = total_productos * Decimal('0.5')
    
    # Redondear para evitar decimales extranos
    total_a_pagar = total_a_pagar.quantize(Decimal('1'))
    
    form = CompraForm(initial={
        'metodo_pago': metodo,
        'nombre': request.user.first_name,
        'email': request.user.email
    })
    context = {
        'form': form,
        'metodo': metodo,
        'productos': productos,
        'reservas': reservas,
        'total_productos': total_productos,
        'total_reservas': total_reservas,
        'total_carrito': total_carrito,
        'total_a_pagar': total_a_pagar,
    }
    return render(request, 'metodos_pago.html', context)


# IMPORTACIONES NECESARIAS ANADIDAS
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, F
from datetime import datetime
from .models import (
    CarritoProducto, Compra, DetalleCompra, Producto, 
    Cabana, Reserva, PrecioCabana, Festivo
)
from .forms import CompraForm
import html
import sys
import io

# Establecer la codificacion predeterminada para el sistema
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

@login_required
def confirmar_compra(request):
    if request.method == "POST":
        print("Metodo POST recibido en confirmar_compra")
        print("Datos del formulario:", request.POST)
        print("Archivos:", request.FILES)

        if 'comprobante_pago' not in request.FILES:
            print("No se encontro archivo de comprobante_pago en la solicitud")
        
        form = CompraForm(request.POST, request.FILES)
        if form.is_valid():
            print("Formulario valido")
            try:
                import os
                
                # Datos del comprador
                nombre_usuario = form.cleaned_data['nombre']
                email_usuario = form.cleaned_data['email']
                telefono_usuario = form.cleaned_data['telefono']
                metodo_pago = form.cleaned_data['metodo_pago']
                horario_comida = form.cleaned_data.get('horario_comida')
                fecha_entrega = form.cleaned_data.get('fecha_entrega')
                comprobante_pago = form.cleaned_data.get('comprobante_pago')
                
                # Validar que el metodo de pago es valido
                metodos_validos = ['nequi', 'daviplata', 'bancolombia']
                if metodo_pago not in metodos_validos:
                    messages.error(request, "Metodo de pago no valido.")
                    return redirect('metodos_pago')
                
                # Validar el comprobante de pago
                if not comprobante_pago:
                    messages.error(request, "Por favor, sube el comprobante de pago. Esto es obligatorio para confirmar tu compra.")
                    return redirect('metodos_pago')
                
                # Validar el formato del archivo
                if comprobante_pago:
                    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
                    ext = os.path.splitext(comprobante_pago.name)[1].lower()
                    if ext not in valid_extensions:
                        messages.error(request, f"Formato de archivo no valido: {ext}. Por favor usa JPG, PNG o PDF.")
                        return redirect('metodos_pago')
                    
                    # Validar tamano (maximo 5MB)
                    if comprobante_pago.size > 5 * 1024 * 1024:  # 5MB en bytes
                        messages.error(request, f"El archivo es demasiado grande ({comprobante_pago.size/1024/1024:.1f}MB). Maximo 5MB.")
                        return redirect('metodos_pago')
                
                # Mapeo de metodo de pago a codigo y nombre legible
                METHOD_CODES = {
                    'nequi': 'NEQ001',
                    'daviplata': 'DAV001',
                    'bancolombia': 'BAN001'
                }
                METHOD_NAMES = {
                    'nequi': 'Nequi',
                    'daviplata': 'Daviplata',
                    'bancolombia': 'Bancolombia'
                }
                codigo_metodo = METHOD_CODES.get(metodo_pago, 'UNKNOWN')
                nombre_metodo = METHOD_NAMES.get(metodo_pago, 'Desconocido')
                
                # Recalcular totales en el servidor - No confiar en datos del cliente
                productos = CarritoProducto.objects.filter(usuario=request.user)
                reservas_sesion = request.session.get('reservas_carrito', [])

                # Verificacion adicional de seguridad: comprobar si aun hay elementos en el carrito
                if not productos.exists() and len(reservas_sesion) == 0:
                    messages.error(request, "No hay productos ni reservas en el carrito para procesar.")
                    return redirect('resumen_compra')
                
                # Total de productos recalculado
                # Total de productos recalculado
                total_productos = Decimal('0')
                
                for item in productos:
                    producto_actual = get_object_or_404(Producto, id=item.producto.id)
                    presentacion = item.presentacion if item.presentacion else 'Unidad'
                    precio_producto = Decimal(str(producto_actual.get_precio_por_presentacion(presentacion)))
                    precio_total_producto = item.cantidad * precio_producto
                    total_productos += precio_total_producto
                            
                
                # Total de reservas recalculado
                total_reservas = Decimal('0')
                reservas_validas = []
                
                for idx, reserva_data in enumerate(reservas_sesion):
                    # Verificar que la cabana existe
                    try:
                        cabana = Cabana.objects.get(nombre=reserva_data['cabana'])
                        fecha = datetime.strptime(reserva_data['fecha'], '%Y-%m-%d').date()
                        
                        # Verificar que la fecha no este ocupada por otra reserva confirmada
                        if Reserva.objects.filter(cabana=reserva_data['cabana'], fecha=fecha, confirmada=True).exists():
                            messages.error(request, f"La cabana {reserva_data['cabana']} ya no esta disponible para el {fecha}.")
                            continue  # Saltar esta reserva
                            
                        # Recalcular el precio (para evitar manipulaciones)
                        try:
                            precios = PrecioCabana.objects.get(cabana=cabana)
                            es_festivo = Festivo.objects.filter(fecha=fecha).exists()
                            es_fin_semana = fecha.weekday() in [5, 6]
                            
                            if es_festivo:
                                precio_base = precios.precio_festivo
                                precio_persona_adicional = precios.precio_persona_adicional_finde_festivo
                            elif es_fin_semana:
                                precio_base = precios.precio_fin_semana
                                precio_persona_adicional = precios.precio_persona_adicional_finde_festivo
                            else:
                                precio_base = precios.precio_entre_semana
                                precio_persona_adicional = precios.precio_persona_adicional_entre_semana
                            
                            personas_adicionales = int(reserva_data.get('personas_adicionales', 0))
                            precio_adicional = personas_adicionales * Decimal(str(precio_persona_adicional))
                            precio_total_calculado = Decimal(str(precio_base)) + precio_adicional
                            
                            # Guardar la reserva validada
                            reserva_data['precio_calculado'] = precio_total_calculado
                            reserva_data['fecha_obj'] = fecha
                            reservas_validas.append(reserva_data)
                            
                            total_reservas += precio_total_calculado
                        except PrecioCabana.DoesNotExist:
                            messages.error(request, f"No se encontraron precios para la cabana {reserva_data['cabana']}.")
                            return redirect('metodos_pago')
                    
                    except Cabana.DoesNotExist:
                        messages.error(request, f"No se encontro la cabana {reserva_data['cabana']} en la base de datos.")
                        return redirect('metodos_pago')
                    except Exception as e:
                        messages.error(request, f"Error con la reserva de la cabana {reserva_data['cabana']}: {str(e)}")
                        return redirect('metodos_pago')
                
                # Si no quedan reservas validas ni productos, redirigir
                if not reservas_validas and not productos.exists():
                    messages.error(request, "No hay productos o reservas validas para procesar.")
                    return redirect('resumen_compra')
                
                # Total general recalculado
                total = total_productos + total_reservas
                
                if reservas_validas:
                    # 70% del valor de reservas + 100% del valor de productos  
                    total_a_pagar = (total_reservas * Decimal('0.7'))
                else:
                    # 50% del valor de productos
                    total_a_pagar = total_productos * Decimal('0.5')
                
                # Redondear para evitar decimales extraños
                total_a_pagar = total_a_pagar.quantize(Decimal('1'))
                
                # Crear la compra y marcarla como pagada
                try:
                    compra = Compra.objects.create(
                        usuario=request.user,
                        nombre=nombre_usuario,
                        email=email_usuario,
                        telefono=telefono_usuario,
                        total=total,
                        metodo_pago=metodo_pago,
                        horario_comida=horario_comida,
                        fecha_entrega=fecha_entrega,
                        comprobante_pago=comprobante_pago,
                        pagado=True
                    )
                except Exception as e:
                    messages.error(request, f"Error al crear la compra en la base de datos: {str(e)}")
                    return redirect('metodos_pago')
                
                detalles_compra = []
                productos_compra = []
                
               # Registrar cada producto del carrito en DetalleCompra
                for item in productos:
                    try:
                        producto_actual = get_object_or_404(Producto, id=item.producto.id)
                        
                        # ✅ USAR LA PRESENTACIÓN QUE EL USUARIO SELECCIONÓ EN EL CARRITO
                        presentacion = item.presentacion if item.presentacion else 'Unidad'
                        
                        # ✅ OBTENER EL PRECIO SEGÚN LA PRESENTACIÓN SELECCIONADA
                        precio_producto = Decimal(str(producto_actual.get_precio_por_presentacion(presentacion)))
                        
                        # Validar que el precio sea válido
                        if precio_producto <= 0:
                            messages.error(request, f"El producto '{item.producto.nombre}' no tiene un precio válido para la presentación '{presentacion}'.")
                            return redirect('metodos_pago')
                        
                        precio_total_producto = item.cantidad * precio_producto
                        
                        DetalleCompra.objects.create(
                            compra=compra,
                            producto=item.producto,
                            precio_unitario=precio_producto,
                            cantidad=item.cantidad,
                            precio_total=precio_total_producto,
                            presentacion=presentacion  # ✅ USAR LA PRESENTACIÓN CORRECTA
                        )
                        
                        # ✅ INFORMACIÓN CORRECTA PARA EL CORREO Y PDF
                        producto_info = {
                            'nombre': item.producto.nombre,
                            'cantidad': item.cantidad,
                            'precio_unitario': precio_producto,
                            'precio_total': precio_total_producto,
                            'tipo_producto': producto_actual.tipo_producto,
                            'presentacion': presentacion  # ✅ PRESENTACIÓN CORRECTA
                        }
                        productos_compra.append(producto_info)
                        detalles_compra.append(f"- {item.cantidad}x {item.producto.nombre} ({presentacion}) - ${precio_total_producto}")
                        
                    except Exception as e:
                        print(f"Error al procesar producto {item.producto.id}: {str(e)}")
                       

                # Registrar cada reserva valida y confirmarla
                reservas_compra = []
                for reserva_data in reservas_validas:
                    try:
                        # Crear un objeto real de Reserva en la base de datos
                        nueva_reserva = Reserva.objects.create(
                            usuario=request.user,
                            cabana=reserva_data['cabana'],
                            fecha=reserva_data['fecha_obj'],
                            telefono=reserva_data.get('telefono', telefono_usuario),
                            numero_personas=int(reserva_data.get('numero_personas', 2)),
                            personas_adicionales=int(reserva_data.get('personas_adicionales', 0)),
                            precio=reserva_data['precio_calculado'],
                            confirmada=True  # Establecer como confirmada directamente
                        )
                        
                        # Ahora usa este nuevo objeto de base de datos en DetalleCompra
                        DetalleCompra.objects.create(
                            compra=compra,
                            reserva=nueva_reserva,
                            precio_unitario=nueva_reserva.precio,
                            cantidad=1,
                            precio_total=nueva_reserva.precio
                        )
                        
                        reserva_info = {
                            'cabana': nueva_reserva.cabana,
                            'fecha': nueva_reserva.fecha,
                            'personas': nueva_reserva.numero_personas,
                            'personas_adicionales': nueva_reserva.personas_adicionales,
                            'precio': nueva_reserva.precio
                        }
                        reservas_compra.append(reserva_info)
                        detalles_compra.append(f"- Reserva en {nueva_reserva.cabana} para {nueva_reserva.fecha} - ${nueva_reserva.precio}")
                    except Exception as e:
                        print(f"Error al procesar reserva: {str(e)}")
                        # Puedes querer registrar mas detalles para depuracion
                        import traceback
                        traceback.print_exc()

                # Limpiar el carrito despues de procesar todo correctamente
                # 1. Limpiar las reservas de la sesion
                request.session['reservas_carrito'] = []
                request.session.modified = True
                
                # 2. Limpiar productos del carrito
                CarritoProducto.objects.filter(usuario=request.user).delete()
                
                # ENVIO DE CORREOS ELECTRONICOS - Solo al administrador
                try:
                    # Correo al administrador
                    admin_email = getattr(settings, 'ADMIN_EMAIL', settings.EMAIL_HOST_USER)  # CORREGIDO: usar getattr
                    subject_admin = f'Nueva compra: #{compra.id} - {nombre_usuario}'
                    
                    comprobante_url = None
                    if compra.comprobante_pago:
                        comprobante_url = request.build_absolute_uri(compra.comprobante_pago.url)

                    # Contexto para el correo del administrador
                    context_admin = {
                        'compra_id': compra.id,
                        'nombre_cliente': nombre_usuario,
                        'email_cliente': email_usuario,
                        'telefono_cliente': telefono_usuario,
                        'productos': productos_compra,
                        'reservas': reservas_compra,
                        'total_productos': total_productos, 
                        'total_reservas': total_reservas,
                        'total_general': total,
                        'total_a_pagar': total_a_pagar,  # ✅ NUEVO: Anticipo pagado
                        'saldo_pendiente': total - total_a_pagar, 
                        'metodo_pago': nombre_metodo,
                        'horario_comida': horario_comida.strftime('%I:%M %p') if horario_comida else None,
                        'fecha_entrega': fecha_entrega.strftime('%d/%m/%Y') if fecha_entrega else None,
                        'fecha_actual': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'comprobante_url': comprobante_url 
                    }
                    
                    # Renderizar el HTML del correo del administrador
                    html_message_admin = render_to_string('emails/nueva_compra_admin.html', context_admin)
                    plain_message_admin = f"""
NUEVA COMPRA - #{compra.id}

DATOS DEL CLIENTE:
Nombre: {nombre_usuario}
Email: {email_usuario}
Telefono: {telefono_usuario}

DETALLES DE LA COMPRA:
{''.join(detalles_compra)}

Total: ${total}
Metodo de pago: {nombre_metodo}
{f"Fecha de entrega: {fecha_entrega.strftime('%d/%m/%Y')}" if fecha_entrega else ""}
{f"Horario de comida: {horario_comida.strftime('%I:%M %p')}" if horario_comida else ""}
Comprobante de pago: {'Adjunto' if comprobante_pago else 'No adjuntado'}
VALOR A PAGAR: ${total_a_pagar}

Esta notificacion ha sido generada automaticamente.
"""
                    
                    # Enviar correo al administrador
                    send_mail(
                        subject=subject_admin,
                        message=plain_message_admin,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[admin_email],
                        html_message=html_message_admin,
                        fail_silently=True,  # Para que no falle la compra si hay error de correo
                    )
                except Exception as e:
                    # Si hay error en los correos, solo registrar pero no detener la compra
                    print(f"Error al enviar correo al administrador: {str(e)}")
                
                messages.success(request, f"Compra realizada exitosamente! ")
                return redirect('compra_confirmada', compra_id=compra.id)
                
            except Exception as e:
                print(f"Error en confirmar_compra: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, "Error al procesar la compra. Intentalo de nuevo.")
                return redirect('metodos_pago')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('metodos_pago')
    
    # Si no es POST, redirigir
    return redirect('resumen_compra')

    
    

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Compra, DetalleCompra
from .utils import generar_factura_response

# Solo la parte de la vista que cambió - función compra_confirmada

@login_required
def compra_confirmada(request, compra_id):
    # Obtener la compra del usuario
    compra = get_object_or_404(Compra, id=compra_id, usuario=request.user)
    
    # Obtener detalles de la compra
    detalles = DetalleCompra.objects.filter(compra=compra)
    
    # Preparar datos para la plantilla y el PDF
    productos_compra = []
    reservas_compra = []
    total_productos = 0
    total_reservas = 0
    
    for detalle in detalles:
        if detalle.producto:
            producto_actual = detalle.producto
            
            # ✅ SOLUCIÓN: Usar la presentación guardada en la base de datos
            # Si no hay presentación guardada, calcularla como respaldo
            if detalle.presentacion:
                presentacion = detalle.presentacion
            else:
                # Solo como respaldo para registros antiguos sin presentación
                try:
                    precio_copa = float(getattr(producto_actual, 'precio_copa', 0))
                    precio_jarra = float(getattr(producto_actual, 'precio_jarra', 0))
                    precio_detalle = float(detalle.precio_unitario)
                    
                    # CORREGIR EL ORDEN: Copa primero para evitar que siempre sea Jarra
                    if precio_detalle == precio_copa and producto_actual.tipo_producto == 'bebida' and precio_copa > 0:
                        presentacion = 'Copa'
                    elif precio_detalle == precio_jarra and producto_actual.tipo_producto == 'bebida' and precio_jarra > 0:
                        presentacion = 'Jarra'
                    else:
                        presentacion = 'Unidad' if producto_actual.tipo_producto == 'comida' else None
                except (ValueError, TypeError, AttributeError):
                    presentacion = 'Unidad' if producto_actual.tipo_producto == 'comida' else None
                        
            # ✅ USAR LOS DATOS REALES GUARDADOS EN LA BASE DE DATOS
            producto_info = {
                'nombre': producto_actual.nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,  # PRECIO REAL
                'precio_total': detalle.precio_total,        # TOTAL REAL
                'tipo_producto': producto_actual.tipo_producto,
                'presentacion': presentacion
            }
            productos_compra.append(producto_info)
            total_productos += detalle.precio_total
        
        elif detalle.reserva:
            reserva_info = {
                'cabana': detalle.reserva.cabana,
                'fecha': detalle.reserva.fecha,
                'personas': detalle.reserva.numero_personas,
                'personas_adicionales': detalle.reserva.personas_adicionales,
                'precio': detalle.reserva.precio
            }
            reservas_compra.append(reserva_info)
            total_reservas += detalle.precio_total
    
    # Calcular el total a pagar (anticipo) usando la misma lógica
    if reservas_compra:
        # 70% del valor de reservas
        total_a_pagar = (Decimal(str(total_reservas)) * Decimal('0.7')).quantize(Decimal('1'))
    else:
        # 50% del valor de productos  
        total_a_pagar = (Decimal(str(total_productos)) * Decimal('0.5')).quantize(Decimal('1'))
    
    # Si se solicita específicamente el PDF (botón de descarga)
    if request.GET.get('descargar_pdf') == 'true':
        # ✅ CAMBIO PRINCIPAL: Pasar total_a_pagar como parámetro
        response = generar_factura_response(
            compra, 
            productos_compra, 
            reservas_compra, 
            total_productos, 
            total_reservas,
            total_a_pagar  # ← NUEVO PARÁMETRO
        )
        
        try:
            filename = f"Factura_La_Kumbre_{compra.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        except Exception as e:
            pass
        
        return response
    
    saldo_pendiente = Decimal(str(compra.total)) - total_a_pagar
    
    # Contexto para la plantilla
    context = {
        'compra': compra,
        'productos': productos_compra,
        'reservas': reservas_compra,
        'total_productos': total_productos,
        'total_reservas': total_reservas,
        'total_general': compra.total,
        'total_a_pagar': total_a_pagar,
        'saldo_pendiente': saldo_pendiente,
    }
    
    return render(request, 'compra_confirmada.html', context)


# Anadir a views.py
from django.http import JsonResponse
from datetime import datetime
from .models import Cabana, PrecioCabana, Festivo
@login_required
def calcular_precio(request):
    cabana_id = request.GET.get('cabana_id')
    fecha_str = request.GET.get('fecha')
    personas_adicionales = int(request.GET.get('personas_adicionales', 0))
    
    try:
        cabana = get_object_or_404(Cabana, id=cabana_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        
        if fecha < datetime.now().date():
            return JsonResponse({
                'success': False,
                'error': 'No se puede reservar en fechas pasadas.'
            })
        
        precios = PrecioCabana.objects.get(cabana=cabana)
        es_festivo = Festivo.objects.filter(fecha=fecha).exists()
        es_finde = fecha.weekday() in [4, 5]  # Viernes y Sabado
        
        # Determinar precio base segun el dia
        if es_festivo:
            precio_base = float(precios.precio_festivo)
            tipo_dia = 'festivo'
        elif es_finde:
            precio_base = float(precios.precio_fin_semana)
            tipo_dia = 'fin_semana'
        else:
            precio_base = float(precios.precio_entre_semana)
            tipo_dia = 'entre_semana'
        
        # CORRECCION: Determinar precios de personas adicionales
        if precios.es_cabana_especial:
            # Para cabana Cafetal: precios diferenciados
            precio_persona_adicional_entre_semana = float(precios.precio_persona_adicional_entre_semana)
            precio_persona_adicional_finde_festivo = float(precios.precio_persona_adicional_finde_festivo)
        else:
            # Para todas las demas cabanas: 80,000 todos los dias
            precio_persona_adicional_entre_semana = 80000.00
            precio_persona_adicional_finde_festivo = 80000.00
        
        return JsonResponse({
            'success': True,
            'precio_base': precio_base,
            'tipo_dia': tipo_dia,
            'precio_persona_adicional_entre_semana': precio_persona_adicional_entre_semana,
            'precio_persona_adicional_finde_festivo': precio_persona_adicional_finde_festivo,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })