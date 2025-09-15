//
//document.querySelector('.clickable-image').addEventListener('click', function() {
//  const container = this.parentElement;
//  if (container.classList.contains('fullscreen')) {
//    container.classList.remove('fullscreen');
//  } else {
//    container.classList.add('fullscreen');
//  }
//});

const images = document.querySelectorAll('.clickable-image');

images.forEach(function(image) {
  image.addEventListener('click', function() {
    const container = this.parentElement;
    if (container.classList.contains('fullscreen')) {
      container.classList.remove('fullscreen');
    } else {
      container.classList.add('fullscreen');
    }
  });
});

