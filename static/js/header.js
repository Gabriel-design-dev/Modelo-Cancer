document.addEventListener('DOMContentLoaded', function() {
    // Capturar todos los enlaces de la cabecera
    const enlacesCabecera = document.querySelectorAll('#cabecera a');
  
    // Agregar evento de clic a cada enlace de la cabecera
    enlacesCabecera.forEach(enlace => {
      enlace.addEventListener('click', function(e) {
        // Ocultar la cabecera
        document.getElementById('cabecera').style.display = 'none';
  
        // Esperar un breve período antes de mostrar la cabecera nuevamente
        setTimeout(function() {
          document.getElementById('cabecera').style.display = 'block';
        }, 500); // Puedes ajustar el tiempo de espera (en milisegundos) según tus necesidades
  
        // Navegar a la sección correspondiente
        const target = this.getAttribute('href');
        document.querySelector(target).scrollIntoView({
          behavior: 'smooth'
        });
  
        // Prevenir el comportamiento predeterminado del enlace
        e.preventDefault();
      });
    });
  });
  