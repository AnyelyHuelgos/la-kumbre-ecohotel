// Crea un archivo: js/protection.js
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('keydown', function(e) {
    if (e.keyCode == 123 || 
        (e.ctrlKey && e.shiftKey && e.keyCode == 73) || 
        (e.ctrlKey && e.keyCode == 85)) {
        e.preventDefault();
    }
});