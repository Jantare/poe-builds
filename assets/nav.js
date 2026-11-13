/* Menu de seções preso no topo, seção atual destacada e botão de voltar ao topo. */
(function () {
  var root = document.documentElement;
  var top = document.querySelector('.topbar'), sec = document.querySelector('nav.sec');
  function measure() {
    if (top) root.style.setProperty('--topbar-h', top.offsetHeight + 'px');
    root.style.setProperty('--secnav-h', (sec ? sec.offsetHeight : 0) + 'px');
  }
  measure(); window.addEventListener('resize', measure);
  var btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'totop'; btn.setAttribute('aria-label', 'Voltar ao topo'); btn.textContent = '↑';
  btn.addEventListener('click', function () { window.scrollTo({ top: 0 }); });
  document.body.appendChild(btn);
  var links = sec ? [].slice.call(sec.querySelectorAll('a[href^="#"]')) : [];
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function onScroll() {
    btn.classList.toggle('show', window.scrollY > 600);
    if (!links.length) return;
    var line = (sec ? sec.getBoundingClientRect().bottom : 0) + 40, cur = -1;
    targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top <= line) cur = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) cur = links.length - 1;
    links.forEach(function (a, i) {
      if (i === cur) {
        a.setAttribute('aria-current', 'true');
        if (sec.scrollWidth > sec.clientWidth) {
          var l = a.offsetLeft - sec.offsetLeft, r = l + a.offsetWidth;
          if (l < sec.scrollLeft) sec.scrollLeft = l - 12;
          else if (r > sec.scrollLeft + sec.clientWidth) sec.scrollLeft = r - sec.clientWidth + 12;
        }
      }
      else a.removeAttribute('aria-current');
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
})();
