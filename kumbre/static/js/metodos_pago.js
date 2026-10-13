document.addEventListener('DOMContentLoaded', function() {
    // ========== ELEMENTOS DEL DOM ==========
    const paymentTabs = document.querySelectorAll('.payment-tab');
    const paymentContents = document.querySelectorAll('.payment-content');
    const paymentMethodInput = document.getElementById('id_metodo_pago');
    const selectedMethodDisplay = document.getElementById('selected-method-display');
    const paymentAmountElements = document.querySelectorAll('.payment-amount');
    const fechaEntregaInput = document.getElementById('id_fecha_entrega');
    const selectPaymentBtn = document.querySelector('.btn[data-toggle="modal"]');
    const paymentModal = document.getElementById('paymentModal');
    const form = document.querySelector('form[action*="confirmar_compra"]');
    const timeInput = document.getElementById('id_horario_comida');
    const timeContainer = document.querySelector('.food-time-container');
    
    // ========== INICIALIZACIÓN ==========
    // Establecer valores de pago
    const monto = obtenerMontoPago();
    paymentAmountElements.forEach(el => {
        el.textContent = Number(monto).toLocaleString();
    });
    
    // Inicializar campo de fecha si existe
    if (fechaEntregaInput) {
        initializeDateField();
    }
    
    // Inicializar códigos QR
    cargarQRCodes();
    
    // Comprobar si hay productos alimenticios
    const hasProducts = document.getElementById('debug-info') && 
                       document.getElementById('debug-info').textContent.includes('Productos:') &&
                       !document.getElementById('debug-info').textContent.includes('Productos: 0');
    
    if (timeContainer) {
        timeContainer.style.display = hasProducts ? 'block' : 'none';
    }

    
        // ========== GESTIÓN DEL MODAL ==========
        if (paymentModal) {
            // Función para abrir modal con animación
            function openModal() {
                paymentModal.style.display = 'flex';
                setTimeout(() => {
                    paymentModal.classList.add('show');
                }, 10);
            }
        
            // Función para cerrar modal con animación
            function closeModal() {
                paymentModal.classList.remove('show');
                setTimeout(() => {
                    paymentModal.style.display = 'none';
                }, 300);
            }
            
            // Configurar botones para abrir modal
            if (selectPaymentBtn) {
                selectPaymentBtn.addEventListener('click', openModal);
            }
            
            // Configurar botones para cerrar modal
            const modalCloseButtons = document.querySelectorAll('[data-dismiss="modal"]');
            modalCloseButtons.forEach(button => {
                button.addEventListener('click', closeModal);
            });
            
            // Cerrar modal al hacer clic fuera
            window.addEventListener('click', function(event) {
                if (event.target === paymentModal) {
                    closeModal();
                }
            });
        }
    
    // ========== VALIDACIÓN DEL FORMULARIO ==========
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevenir envío por defecto para validación
            
            let isValid = true;
            const inputs = form.querySelectorAll('input[required]');
            
            // Verificar cada input requerido
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('invalid');
                    
                    // Animación de error
                    input.classList.add('shake');
                    setTimeout(() => {
                        input.classList.remove('shake');
                    }, 600);
                } else {
                    input.classList.remove('invalid');
                }
            });
            
            // Verificar si se seleccionó método de pago
            if (paymentMethodInput && !paymentMethodInput.value) {
                isValid = false;
                // Mostrar alerta
                alert('Por favor seleccione un método de pago');
                // Resaltar botón de pago
                if (selectPaymentBtn) {
                    selectPaymentBtn.classList.add('shake');
                    setTimeout(() => {
                        selectPaymentBtn.classList.remove('shake');
                    }, 600);
                }
            }
            
            // Verificar comprobante de pago si existe
            const comprobanteInput = document.getElementById('id_comprobante_pago');
            if (comprobanteInput && comprobanteInput.getAttribute('required') !== null && comprobanteInput.files.length === 0) {
                isValid = false;
                alert('Por favor, suba un comprobante de pago');
                comprobanteInput.classList.add('invalid');
            }
            
            if (isValid) {
                // Mostrar animación de éxito antes de enviar
                const successOverlay = document.createElement('div');
                successOverlay.className = 'success-overlay';
                successOverlay.innerHTML = '<div class="success-checkmark"></div><p>¡Procesando su compra!</p>';
                document.body.appendChild(successOverlay);
                
                // Enviar formulario después de la animación
                setTimeout(() => {
                    form.removeEventListener('submit', arguments.callee);
                    form.submit();
                }, 1500);
            }
        });
        
        // Validación en tiempo real
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.classList.add('invalid');
                } else {
                    this.classList.remove('invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('invalid');
                }
            });
        });
    }
    
    
    
    // ========== EFECTOS VISUALES ==========
    // Añadir efecto hover a los elementos de la lista
    const listItems = document.querySelectorAll('.list-group-item');
    listItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.1)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.1)';
        });
    });

    // Añadir efecto ripple a los botones
    const buttons = document.querySelectorAll('.btn, .boton1, .payment-method-button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});


// ========== FUNCIONES PARA ACCIONES DE USUARIO ==========
function obtenerMontoPago() {
    // Primero intentar obtener del elemento de pago anticipado
    const advanceElement = document.getElementById('advance-payment-amount');
    if (advanceElement && advanceElement.textContent.trim()) {
        return advanceElement.textContent.trim().replace(/[^\d]/g, '');
    }
    
    // Si no, obtener del total mostrado en la página
    const totalElement = document.querySelector('.total .para');
    if (totalElement) {
        const totalText = totalElement.textContent;
        const matches = totalText.match(/\$\s*([\d,\.]+)/);
        if (matches && matches[1]) {
            // Eliminar comas del número
            const totalSinFormato = matches[1].replace(/,/g, '');
            
            // Verificar si hay reservas para calcular porcentaje
            const hayReservas = document.querySelectorAll('.list-group-item').length > 0 && 
                              Array.from(document.querySelectorAll('.list-group-item')).some(item => 
                                  item.textContent.includes('Reserva:')
                              );
            
            if (hayReservas) {
                // Para reservas, calcular 70%
                return Math.round(parseFloat(totalSinFormato) * 0.7);
            } else {
                // Para productos solo, pago completo
                return Math.round(parseFloat(totalSinFormato));
            }
        }
    }
    
    console.warn("No se pudo determinar el monto del pago, usando valor por defecto");
    return "0"; // Valor por defecto si no se puede determinar
}

function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto)
        .then(() => {
            // Crear y mostrar una notificación toast
            const toast = document.createElement('div');
            toast.className = 'copy-toast';
            toast.textContent = '¡Número copiado!';
            document.body.appendChild(toast);
            
            // Mostrar y ocultar con animación
            setTimeout(() => toast.classList.add('show'), 10);
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 2000);
        })
        .catch(err => {
            console.error('Error al copiar: ', err);
            alert('No se pudo copiar el número: ' + err);
        });
}


























    // Función mejorada para obtener y mostrar el monto a pagar
document.addEventListener('DOMContentLoaded', function() {
    // Calcular y actualizar el monto a pagar inmediatamente después de cargar la página
    actualizarMontoPago();
});
<!-- 1. Modifica esta parte en tu HTML para cambiar el texto según hay reservas o no -->
<div class="cart-totals">
    {% if productos %}
        <div class="subtotal">
            <strong>Subtotal Productos:</strong> ${{ total_productos }}
        </div>
    {% endif %}
    
    {% if reservas %}
        <div class="subtotal">
            <strong>Subtotal Reservas:</strong> ${{ total_reservas }}
        </div>
    {% endif %}
    
    <div class="total">
        <p class="para"><strong>Total:</strong> ${{ total_carrito }}</p>
    </div>

   
    <div class="reservation-note">
        {% if reservas %}
            <p>Para hacer válida su reserva debe cancelar el 70% del precio total de la cabaña.</p>
            <!-- Calculamos el valor a cancelar desde el servidor (70% de reservas + 100% de productos) -->
            <p class="advance-payment"><strong>Valor a cancelar:</strong> $<span id="advance-payment-amount">{{ total_a_pagar }}</span></p>
        {% else %}
            <p>Para confirmar su pedido debe cancelar el 50% del precio total de los productos.</p>
            <!-- Calculamos el valor a cancelar desde el servidor (50% del total) -->
            <p class="advance-payment"><strong>Valor a cancelar:</strong> $<span id="advance-payment-amount">{{ total_a_pagar }}</span></p>
        {% endif %}
    </div>
</div>

// Esta función debe ejecutarse automáticamente al cargar la página
function actualizarMontoPago() {
    const advanceElement = document.getElementById('advance-payment-amount');
    if (advanceElement) {
        // Verificar si hay reservas
        const hayReservas = document.querySelectorAll('.list-group-item')
            .length > 0 && Array.from(document.querySelectorAll('.list-group-item'))
            .some(item => item.textContent.includes('Reserva:'));
            
        // Verificar si hay productos
        const hayProductos = document.querySelectorAll('.list-group-item')
            .length > 0 && Array.from(document.querySelectorAll('.list-group-item'))
            .some(item => item.textContent.includes('Producto:'));
        
        // Obtener los totales
        let totalReservas = 0;
        let totalProductos = 0;
        
        // Si hay un elemento que muestra el subtotal de reservas, extraer su valor
        const subtotalReservasElement = document.querySelector('.subtotal:contains("Subtotal Reservas:")');
        if (subtotalReservasElement) {
            const match = subtotalReservasElement.textContent.match(/\$\s*([\d,]+(\.\d+)?)/);
            if (match && match[1]) {
                totalReservas = parseFloat(match[1].replace(/,/g, ''));
            }
        }
        
        // Si hay un elemento que muestra el subtotal de productos, extraer su valor
        const subtotalProductosElement = document.querySelector('.subtotal:contains("Subtotal Productos:")');
        if (subtotalProductosElement) {
            const match = subtotalProductosElement.textContent.match(/\$\s*([\d,]+(\.\d+)?)/);
            if (match && match[1]) {
                totalProductos = parseFloat(match[1].replace(/,/g, ''));
            }
        }
        
        // Si no tenemos los subtotales específicos, intenta obtener el total general
        if (totalReservas === 0 && totalProductos === 0) {
            const totalElement = document.querySelector('.total .para');
            if (totalElement) {
                const totalMatch = totalElement.textContent.match(/\$\s*([\d,]+(\.\d+)?)/);
                if (totalMatch && totalMatch[1]) {
                    const totalCarrito = parseFloat(totalMatch[1].replace(/,/g, ''));
                    
                    // Asignar el total según lo que tenemos
                    if (hayReservas && !hayProductos) {
                        totalReservas = totalCarrito;
                    } else if (hayProductos && !hayReservas) {
                        totalProductos = totalCarrito;
                    } else if (hayReservas && hayProductos) {
                        // Si tenemos ambos pero no sabemos la proporción, asumimos mitad y mitad
                        // (esto es un fallback, normalmente deberíamos tener los subtotales)
                        totalReservas = totalCarrito / 2;
                        totalProductos = totalCarrito / 2;
                    }
                }
            }
        }
        
        // Calcular el monto a pagar según las reglas:
        let montoPago = 0;
        
        if (hayReservas) {
            // Para reservas: 70% del valor de reservas + 100% del valor de productos
            montoPago = (totalReservas * 0.7) + totalProductos;
            
            // Actualizar el texto explicativo
            const noteElement = document.querySelector('.reservation-note p');
            if (noteElement) {
                noteElement.textContent = 'Para hacer válida su reserva debe cancelar el 70% del precio total de la cabaña.';
            }
        } else if (hayProductos) {
            // Si solo hay productos: 50% del valor total
            montoPago = totalProductos * 0.5;
            
            // Actualizar el texto explicativo
            const noteElement = document.querySelector('.reservation-note p');
            if (noteElement) {
                noteElement.textContent = 'Para confirmar su pedido debe cancelar el 50% del precio total de los productos.';
            }
        }
        
        // Redondear para evitar decimales extraños
        montoPago = Math.round(montoPago);
        
        // Actualizar el valor mostrado
        advanceElement.textContent = montoPago.toLocaleString();
        console.log('Monto actualizado a: ' + montoPago);
    }
}

// Ejecutar la función al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    actualizarMontoPago();
});

// También ejecutar la función cuando cambian los elementos del carrito
// (esto puede ser útil si tienes funcionalidad para modificar el carrito en la misma página)
const carritoItems = document.querySelectorAll('.list-group-item');
if (carritoItems.length > 0) {
    carritoItems.forEach(item => {
        item.addEventListener('change', actualizarMontoPago);
    });
}
});
// Add necessary CSS styles for animations and effects
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        /* Modal styles */
        #paymentModal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        #paymentModal.show {
            opacity: 1;
        }
        
        .modal-content {
            background-color: white;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            transform: scale(0.9);
            transition: transform 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        
        #paymentModal.show .modal-content {
            transform: scale(1);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
        }
        
        .modal-body {
            padding: 20px;
        }
        
        /* Button styles */
        .payment-method-button {
            display: block;
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background-color: white;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            text-align: left;
            display: flex;
            align-items: center;
        }
        
        .payment-method-button:hover {
            border-color: #7e57c2;
            background-color: #f5f2ff;
        }
        
        .payment-method-button.active {
            border-color: #5e35b1;
            background-color: #ede7f6;
        }
        
        .payment-method-button svg {
            margin-right: 10px;
        }
        
        /* Ripple effect */
        .ripple {
            position: absolute;
            background-color: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            width: 10px;
            height: 10px;
        }
        
        @keyframes ripple {
            to {
                transform: scale(20);
                opacity: 0;
            }
        }
        
        /* Animation styles */
        .shake {
            animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
        }
        
        @keyframes shake {
            10%, 90% { transform: translateX(-1px); }
            20%, 80% { transform: translateX(2px); }
            30%, 50%, 70% { transform: translateX(-4px); }
            40%, 60% { transform: translateX(4px); }
        }
        
        .invalid {
            border-color: #ff6b6b !important;
            background-color: rgba(255, 107, 107, 0.05) !important;
        }
        
        .success-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.9);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .success-checkmark {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: block;
            stroke-width: 2;
            stroke: #4bb71b;
            stroke-miterlimit: 10;
            box-shadow: inset 0px 0px 0px #4bb71b;
            animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both;
            position: relative;
            margin: 0 auto 15px;
        }
        
        .success-checkmark:before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(45deg);
            width: 30px;
            height: 60px;
            border-bottom: 6px solid #4bb71b;
            border-right: 6px solid #4bb71b;
        }
        
        @keyframes fill {
            100% { box-shadow: inset 0px 0px 0px 30px #4bb71b; }
        }
        
        @keyframes scale {
            0%, 100% { transform: none; }
            50% { transform: scale(1.1); }
        }
        
        .selected-payment-animation {
            animation: bounce 0.5s ease;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }
        
        /* Payment method image styles */
        .payment-method-img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        #modal-method-image {
            margin-top: 20px;
            text-align: center;
        }
        
        #selected-method-display {
            margin-top: 10px;
            text-align: center;
        }
        
        /* Estilos para el calendario */
        .fecha-entrega-container {
            margin: 15px 0;
            transition: all 0.3s ease;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .fecha-entrega-container:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        #id_fecha_entrega {
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            width: 100%;
            color: #333;
            background-color: white;
            transition: border-color 0.2s ease;
        }
        
        #id_fecha_entrega:hover, #id_fecha_entrega:focus {
            border-color: #7e57c2;
            outline: none;
        }
        
        .fecha-entrega-container label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #444;
        }
        
        .fecha-entrega-container small {
            display: block;
            margin-top: 5px;
            color: #666;
        }
    `;
    document.head.appendChild(style);
});
