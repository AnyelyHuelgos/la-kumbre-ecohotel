from pyexpat import model
from django.contrib import admin 
from .models import Sugerencia
from .models import Usuario 
from .models import Cabana, Reserva  # Asegúrate de importar el modelo correcto
from .models import Producto
from .models import Compra, DetalleCompra


# Register your models here.

@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ("username", "telefono", "categoria")
    search_fields = ("username", "telefono", "categoria")


@admin.register(Cabana)
class CabanaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio','created_at')  # Muestra estos campos en la lista
    list_filter = ('created_at',)  


admin.site.register(Usuario) 

class ReservaAdmin(admin.ModelAdmin):
    list_display = ( "cabana", "fecha")  # Muestra estas columnas en la tabla
    list_filter = ('estado',) 

admin.site.register(Reserva, ReservaAdmin)

admin.site.register(Producto)



from django.contrib import admin
from django.utils.html import format_html
from .models import Compra, DetalleCompra, Reserva, Cabana, Producto, CarritoProducto, Sugerencia, Usuario, PrecioCabana, Festivo

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ['producto', 'reserva', 'precio_unitario', 'cantidad', 'precio_total']
    can_delete = False

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'nombre', 'email', 'total', 'metodo_pago', 'pagado', 'fecha_creacion', 'mostrar_comprobante']
    list_filter = ['pagado', 'fecha_creacion', 'metodo_pago']
    search_fields = ['nombre', 'email', 'usuario__username']
    readonly_fields = ['mostrar_comprobante_grande']
    inlines = [DetalleCompraInline]
    
    def mostrar_comprobante(self, obj):
        if obj.comprobante_pago:
            if obj.comprobante_pago.url.lower().endswith('.pdf'):
                return format_html('<a href="{}" target="_blank" class="button">Ver PDF</a>', obj.comprobante_pago.url)
            else:
                return format_html('<a href="{}" target="_blank"><img src="{}" height="50" /></a>', 
                                 obj.comprobante_pago.url, obj.comprobante_pago.url)
        return "No adjuntado"
    mostrar_comprobante.short_description = 'Comprobante'
    
    def mostrar_comprobante_grande(self, obj):
        if obj.comprobante_pago:
            if obj.comprobante_pago.url.lower().endswith('.pdf'):
                return format_html('<a href="{}" target="_blank" class="button">Ver PDF</a>', obj.comprobante_pago.url)
            else:
                return format_html('<img src="{}" style="max-width:100%; max-height:500px;" />', obj.comprobante_pago.url)
        return "No hay comprobante adjunto."
    mostrar_comprobante_grande.short_description = 'Comprobante de Pago'
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('usuario', 'nombre', 'email', 'telefono')
        }),
        ('Información de Pago', {
            'fields': ('total', 'metodo_pago', 'pagado', 'horario_comida')
        }),
        ('Comprobante de Pago', {
            'fields': ('comprobante_pago', 'mostrar_comprobante_grande')
        }),
    )




from django.contrib import admin
from .models import Cabana, PrecioCabana, Festivo, Reserva

class PrecioCabanaAdmin(admin.ModelAdmin):
    list_display = ('cabana', 'precio_entre_semana', 'precio_fin_semana', 'precio_festivo')
    search_fields = ('cabana__nombre',)

class FestivoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'descripcion')
    list_filter = ('fecha',)
    search_fields = ('descripcion',)

admin.site.register(PrecioCabana, PrecioCabanaAdmin)
admin.site.register(Festivo, FestivoAdmin)