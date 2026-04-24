document.addEventListener('DOMContentLoaded', function() {
    // Funciones para manejar los modales
    function setupModal(btnId, modalId) {
        var btn = document.getElementById(btnId);
        var modal = document.getElementById(modalId);
        var span = modal.querySelector(".close");
        
        btn.onclick = function() {
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
            
            // Reinicia el slider al abrir el modal (esto sigue funcionando)
            var slides = modal.querySelectorAll('.slide');
            slides.forEach(function(slide) {
                slide.classList.remove('active');
            });
            slides[0].classList.add('active');
        }
        
        span.onclick = function() {
            modal.style.display = "none";
            document.body.style.overflow = "auto";
        }
        
        window.addEventListener('click', function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
                document.body.style.overflow = "auto";
            }
        });
        
        // Configuración de los botones de navegación del slider
        var prevBtn = modal.querySelector('.prev-button');
        var nextBtn = modal.querySelector('.next-button');
        var slides = modal.querySelectorAll('.slide');
        
        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', function() {
                var activeSlide = modal.querySelector('.slide.active');
                var prevSlide = activeSlide.previousElementSibling || slides[slides.length - 1];
                
                activeSlide.classList.remove('active');
                prevSlide.classList.add('active');
            });
            
            nextBtn.addEventListener('click', function() {
                var activeSlide = modal.querySelector('.slide.active');
                var nextSlide = activeSlide.nextElementSibling || slides[0];
                
                activeSlide.classList.remove('active');
                nextSlide.classList.add('active');
            });
        }
    }
    
    // Configuración de los carruseles de imágenes - SOLO para desktop
    function setupCarousels() {
        var carousels = document.querySelectorAll('.carousel');
        
        carousels.forEach(function(carousel) {
            var images = carousel.querySelector('.carousel-images');
            
            function updateCarousel() {
                if (window.innerWidth <= 992) {
                    // En móviles: NO hacer nada, dejar la imagen estática
                    // Remover cualquier event listener previo
                    carousel.replaceWith(carousel.cloneNode(true));
                } else {
                    // En escritorio: comportamiento normal con hover
                    // No es necesario hacer nada adicional ya que el CSS maneja el hover
                }
            }
            
            // Inicializar y actualizar en cada cambio de tamaño
            updateCarousel();
            window.addEventListener('resize', updateCarousel);
        });
    }
    
    // Inicialización de modales
    setupModal('openModalBtn1', 'modalCabaña1');
    setupModal('openModalBtn2', 'modalCabaña2');
    setupModal('openModalBtn3', 'modalCabaña3');
    setupModal('openModalBtn4', 'modalCabaña4');
    setupModal('openModalBtn5', 'modalCabaña5');
    
    // Inicialización de carruseles
    setupCarousels();
});