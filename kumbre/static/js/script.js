document.addEventListener('DOMContentLoaded', function() {
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const slide = document.querySelector('.slide');
    const items = document.querySelectorAll('.slide .item');
    
    // Índice de la imagen actualmente visible en móviles
    let currentMobileIndex = 0;
    
    // Función para comprobar si estamos en vista móvil
    function isMobileView() {
        return window.innerWidth <= 867;
    }
    
    // Función para actualizar la visualización en modo móvil
    function updateMobileView() {
        if (isMobileView()) {
            // Ocultar todas las imágenes
            items.forEach((item, index) => {
                if (index === currentMobileIndex) {
                    // Estilos para que sean iguales a las dos primeras imágenes en móvil
                    item.style.display = 'block';
                    item.style.position = 'absolute';
                    item.style.top = '0';
                    item.style.left = '0';
                    item.style.transform = 'translate(0, 0)';
                    item.style.width = '100%';
                    item.style.height = '100%';
                    item.style.borderRadius = '0';
                    item.style.zIndex = '1';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Mostrar contenido de la imagen actual si existe
            const currentContent = items[currentMobileIndex].querySelector('.content');
            if (currentContent) {
                currentContent.style.display = 'block';
            }
        } else {
            // Restaurar la visualización normal para escritorio
            items.forEach(item => {
                item.style.display = '';
                item.style.position = '';
                item.style.top = '';
                item.style.left = '';
                item.style.transform = '';
                item.style.width = '';
                item.style.height = '';
                item.style.borderRadius = '';
                item.style.zIndex = '';
            });
        }
    }
    
    // Inicializar la vista inmediatamente
    updateMobileView();
    
    // Manejar el botón "Siguiente"
    nextBtn.addEventListener('click', function() {
        if (isMobileView()) {
            // Incrementar el índice y manejar el ciclo
            currentMobileIndex = (currentMobileIndex + 1) % items.length;
            updateMobileView();
        } else {
            // Comportamiento original del slider para escritorio
            let firstItem = slide.firstElementChild;
            slide.appendChild(firstItem);
        }
    });
    
    // Manejar el botón "Anterior"
    prevBtn.addEventListener('click', function() {
        if (isMobileView()) {
            // Decrementar el índice y manejar el ciclo
            currentMobileIndex = (currentMobileIndex - 1 + items.length) % items.length;
            updateMobileView();
        } else {
            // Comportamiento original del slider para escritorio
            let lastItem = slide.lastElementChild;
            slide.prepend(lastItem);
        }
    });
    
    // Volver a calcular cuando cambie el tamaño de la ventana
    window.addEventListener('resize', updateMobileView);
});