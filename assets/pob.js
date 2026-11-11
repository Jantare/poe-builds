/* "Copiar código do PoB": carrega o código ao abrir a página e copia no clique. */
(function () {
  document.querySelectorAll('[data-pob]').forEach(function (btn) {
    var code = null, box = document.getElementById(btn.getAttribute('aria-controls'));
    fetch(btn.getAttribute('data-pob')).then(function (r) { return r.text(); }).then(function (t) { code = t.trim(); btn.disabled = false; });
    btn.disabled = true;
    btn.addEventListener('click', function () {
      if (!code) return;
      var done = function () { var o = btn.textContent; btn.textContent = 'Código copiado'; setTimeout(function () { btn.textContent = o; }, 2500); };
      var fallback = function () { if (box) { box.hidden = false; box.value = code; box.focus(); box.select(); } };
      try { navigator.clipboard.writeText(code).then(done, fallback); } catch (e) { fallback(); }
    });
  });
})();
