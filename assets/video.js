/* Showcase: mostra só a miniatura até o clique, depois carrega o player do YouTube. */
document.querySelectorAll('.yt[data-id]').forEach(function (el) {
  el.addEventListener('click', function () {
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + el.getAttribute('data-id') + '?autoplay=1&rel=0';
    f.title = el.getAttribute('aria-label') || 'Vídeo';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    el.replaceWith(f);
  });
});
