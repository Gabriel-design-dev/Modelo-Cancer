window.addEventListener('DOMContentLoaded', function() {
    // Inicializar ScrollReveal
    window.sr = ScrollReveal();
  
    // Configurar animaciones para los campos específicos
    sr.reveal('.navegaciones', {
      duration: 3000,
      origin: 'left',
      distance: '-100px'
    });
  
    sr.reveal('.infojs', {
      duration: 4000,
      origin: 'bottom',
      distance: '-100px'
    });
  
    sr.reveal('.info2js', {
      duration: 4000,
      origin: 'left',
      distance: '480px'
    });
  
    sr.reveal('.info3js', {
      duration: 4000,
      origin: 'right',
      distance: '480px'
    });
  });
  


