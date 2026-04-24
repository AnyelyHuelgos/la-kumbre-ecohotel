from django.db import models
from django.contrib.auth.models import User

class Sugerencia(models.Model):
    CATEGORIAS = [
        ('Servicio', 'Servicio'),
        ('Instalaciones', 'Instalaciones'),
        ('Comida', 'Comida'),
    ]
    
    username = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, default='')
    sugerencia = models.TextField()
    categoria = models.CharField(max_length=50, choices=CATEGORIAS)

    def __str__(self): 
        return f"{self.username} - {self.categoria}"
    
class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    telefono = models.CharField(max_length=15)


class Cabana(models.Model):  # Corrige el nombre del modelo
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.nombre
    

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cabana = models.CharField(max_length=100)  # Nombre de la cabaña
    fecha = models.DateField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) # Precio de la cabaña
    telefono = models.CharField(max_length=15)  # Teléfono del usuario
    numero_personas = models.PositiveIntegerField()  # Número de personas en la reserva
    personas_adicionales = models.PositiveIntegerField(default=0)  # Número de personas adicionales
    precio_personas_adicionales = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Precio por personas adicionales
    estado = models.CharField(max_length=50, choices=[('Pendiente', 'Pendiente'), ('Aprobada', 'Aprobada')])
    confirmada = models.BooleanField(default=False)  

    class Meta:
        unique_together = ('cabana', 'fecha')

    def clean(self):
        # Si ya existe una reserva para la misma cabana y fecha (excluyendo la misma instancia en caso de edición)
        if Reserva.objects.filter(cabana=self.cabana, fecha=self.fecha).exclude(pk=self.pk).exists():
            raise ValidationError("La cabaña ya está reservada para esa fecha.")

    def __str__(self):
        return f"Reserva de {self.cabana} para {self.fecha}"
        
        
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal


class Producto(models.Model):
    TIPO_CHOICES = [
        ('comida', 'Comida'),
        ('bebida', 'Bebida'),
    ]
    
    PRESENTACION_CHOICES = [
        ('copa', 'Copa'),
        ('jarra', 'Jarra'),
    ]
    
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo_producto = models.CharField(max_length=10, choices=TIPO_CHOICES, default='comida')
    
    # Precios - OPCION 1: Permitir NULL
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.0)  # Para comidas
    precio_copa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Para bebidas
    precio_jarra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Para bebidas
    
    # Campo para saber si el producto esta anadido al carrito
    en_carrito = models.BooleanField(default=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nombre
    
    def get_precio_por_presentacion(self, presentacion=None):
        """Devuelve el precio segun la presentacion para bebidas, o precio normal para comidas"""
        if self.tipo_producto == 'bebida' and presentacion:
            if presentacion == 'copa' and self.precio_copa is not None:
                return self.precio_copa
            elif presentacion == 'jarra' and self.precio_jarra is not None:
                return self.precio_jarra
            # Si no hay precio especifico, retorna el precio base si existe
            return self.precio if self.precio is not None else 0
        # Para comidas
        return self.precio if self.precio is not None else 0
    
    def clean(self):
        """Validacion personalizada"""
        from django.core.exceptions import ValidationError
        
        if self.tipo_producto == 'comida':
            if not self.precio or self.precio <= 0:
                raise ValidationError('Las comidas deben tener un precio base.')
        
        if self.tipo_producto == 'bebida':
            if not self.precio_copa and not self.precio_jarra:
                raise ValidationError('Las bebidas deben tener al menos un precio (copa o jarra).')


class CarritoProducto(models.Model):
    PRESENTACION_CHOICES = [
        ('copa', 'Copa'),
        ('jarra', 'Jarra'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    presentacion = models.CharField(max_length=10, choices=PRESENTACION_CHOICES, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        if self.presentacion:
            return f"{self.producto.nombre} - {self.get_presentacion_display()} ({self.cantidad})"
        return f"{self.producto.nombre} ({self.cantidad})"
    
    def get_total(self):
        return self.precio_unitario * self.cantidad
    
    def save(self, *args, **kwargs):
        # SIEMPRE recalcular el precio al guardar
        self.precio_unitario = self.producto.get_precio_por_presentacion(self.presentacion)
        super().save(*args, **kwargs)
        


class Compra(models.Model):
    METODO_PAGO_CHOICES = [
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('bancolombia', 'Bancolombia'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    fecha_entrega = models.DateField(null=True, blank=True)
    horario_comida = models.TimeField(null=True, blank=True)
    pagado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # Añadir al modelo Compra en models.py
    comprobante_pago = models.ImageField(upload_to='comprobantes_pago/', null=True, blank=True)
    
    def __str__(self):
        return f"Compra #{self.id} de {self.usuario.username}"
    

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    # El detalle puede estar asociado a un producto o a una reserva.
    # Se usa SET_NULL para que si se elimina el producto o la reserva, el detalle conserve la información.
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True, blank=True)
    reserva = models.ForeignKey('Reserva', on_delete=models.SET_NULL, null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)  # Se puede calcular como precio_unitario * cantidad
    presentacion = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        if self.producto:
            return f"{self.cantidad} x {self.producto.nombre}"
        elif self.reserva:
            return f"Reserva: {self.reserva.cabana} para {self.reserva.fecha}"
        return "Detalle sin asignar"
        
    # ✅ NUEVO MÉTODO save() PARA CALCULAR CORRECTAMENTE EL PRECIO
    def save(self, *args, **kwargs):
        # Solo calcular precio si hay un producto y no se ha establecido precio_unitario
        if self.producto and (self.precio_unitario is None or self.precio_unitario == 0):
            self.precio_unitario = self.producto.get_precio_por_presentacion(self.presentacion)
        
        # Calcular precio total
        if self.precio_unitario and self.cantidad:
            self.precio_total = self.precio_unitario * self.cantidad
            
        super().save(*args, **kwargs)



# Añadir a models.py
class PrecioCabana(models.Model):
    cabana = models.ForeignKey(Cabana, on_delete=models.CASCADE, related_name='precios')
    precio_entre_semana = models.DecimalField(max_digits=10, decimal_places=2)
    precio_fin_semana = models.DecimalField(max_digits=10, decimal_places=2)
    precio_festivo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_persona_adicional_entre_semana = models.DecimalField(max_digits=10, decimal_places=2, default=60000.00)
    precio_persona_adicional_finde_festivo = models.DecimalField(max_digits=10, decimal_places=2, default=80000.00)
    es_cabana_especial = models.BooleanField(default=False, help_text="Marcar si esta cabana tiene precios diferenciados para personas adicionales")


    def __str__(self):
        return f"Precios para {self.cabana.nombre}"

class Festivo(models.Model):
    fecha = models.DateField(unique=True)
    descripcion = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d')} - {self.descripcion}"