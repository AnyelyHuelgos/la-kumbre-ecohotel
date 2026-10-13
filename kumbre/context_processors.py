
def cart_counter(request):
    """Context processor para contar items en el carrito (productos y reservas)"""
    total_items = 0
    
    # Contar productos
    if request.user.is_authenticated:
        from .models import CarritoProducto
        productos_count = CarritoProducto.objects.filter(usuario=request.user).count()
        total_items += productos_count
    
    # Contar reservas en sesi¨®n
    reservas_count = len(request.session.get('reservas_carrito', []))
    total_items += reservas_count
    
    return {
        'cart_count': total_items
    }