/* Visualizador de gemas estilo pobb.in: um ato/fase por vez (seletor) e dica com nível e onde conseguir a gema.
   Sem JS, mostra todos os atos. Dados de onde conseguir: exile-leveling (MIT). */
(function () {
  var views = [].slice.call(document.querySelectorAll('.pobview'));
  var tip = document.createElement('div'); tip.className = 'pvtip'; tip.hidden = true; tip.setAttribute('role', 'tooltip');
  document.body.appendChild(tip);
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function tipHtml(name, d, cls, color) {
    var h = '<div class="pvth"><b class="c-' + color + '">' + esc(name) + '</b>' + (d && d.l ? '<span>Nível mínimo ' + d.l + '</span>' : '') + '</div>';
    if (d && d.k) {
      var tf = d.k.indexOf('transfig') >= 0, vl = d.k.indexOf('vaal') >= 0;
      h += '<p>' + (tf && vl ? 'Versão Vaal de gema transfigurada: transforme a ' + esc(d.b) + ' na Divine Font do Labirinto e corrompa com Vaal Orb, ou compre no trade.' :
        tf ? 'Gema transfigurada: troque a ' + esc(d.b) + ' na Divine Font do Labirinto ou compre no trade.' :
        'Versão Vaal: use uma Vaal Orb na ' + esc(d.b) + ' ou compre no trade.') + '</p>';
      if (d.s && d.s.length) h += '<p class="pvsub">A ' + esc(d.b) + ' normal:</p>';
    }
    if (d && d.s && d.s.length) {
      h += '<table>' + d.s.map(function (s) {
        return '<tr><td>Ato ' + s[0] + '</td><td>' + esc(s[1]) + '</td><td>' + esc(s[2]) + '</td><td class="k">' + (s[3] === 'q' ? 'recompensa' : 'compra') + '</td></tr>';
      }).join('') + '</table>';
    } else if (!d || !d.k) {
      h += '<p>Não vem de quest nem de vendor para ' + esc(cls) + ': drop, Labirinto ou trade.</p>';
    }
    return h;
  }
  function place(el) {
    var r = el.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = Math.min(Math.max(8, r.left), window.innerWidth - w - 8), y = r.bottom + 6;
    if (y + h > window.innerHeight - 8) y = Math.max(8, r.top - h - 6);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  var cur = null;
  function show(el) {
    var v = el.closest('.pobview'); if (!v) return;
    if (!v._info) { try { v._info = JSON.parse(v.querySelector('.pvinfo').textContent); } catch (e) { v._info = {}; } }
    var name = el.getAttribute('data-g'), m = /c-(\w)/.exec(el.className);
    tip.innerHTML = tipHtml(name, v._info[name], v.getAttribute('data-cls'), m ? m[1] : 'w');
    tip.hidden = false; place(el); cur = el;
  }
  function hide() { tip.hidden = true; cur = null; }
  document.addEventListener('mouseover', function (ev) { var el = ev.target.closest && ev.target.closest('[data-g]'); if (el) show(el); });
  document.addEventListener('mouseout', function (ev) { var el = ev.target.closest && ev.target.closest('[data-g]'); if (el && !el.contains(ev.relatedTarget)) hide(); });
  document.addEventListener('focusin', function (ev) { var el = ev.target.closest && ev.target.closest('[data-g]'); if (el) show(el); });
  document.addEventListener('focusout', hide);
  document.addEventListener('click', function (ev) {  // toque no celular
    var el = ev.target.closest && ev.target.closest('[data-g]');
    if (el) { if (cur === el && !tip.hidden) hide(); else show(el); } else if (!tip.contains(ev.target)) hide();
  });
  window.addEventListener('scroll', function () { if (cur) place(cur); }, { passive: true });

  views.forEach(function (v) {
    var sets = [].slice.call(v.querySelectorAll('.pvset'));
    var sel = v.querySelector('.pvsel'), count = v.querySelector('.pvcount');
    if (!sel || sets.length < 2) return;
    v.classList.add('js');
    function go(i) {
      i = Math.max(0, Math.min(sets.length - 1, i));
      sets.forEach(function (s, k) { s.classList.toggle('on', k === i); });
      sel.value = String(i);
      if (count) count.textContent = (i + 1) + ' de ' + sets.length;
      hide();
    }
    v._go = function (id) { for (var k = 0; k < sets.length; k++) if (sets[k].id === id) { go(k); return true; } return false; };
    sel.addEventListener('change', function () { go(+sel.value); });
    [].forEach.call(v.querySelectorAll('.pvnav'), function (b) {
      b.addEventListener('click', function () { go(+sel.value + (+b.getAttribute('data-d'))); });
    });
    go(0);
  });
  function fromHash() {  // links tipo #cobra-3 abrem o ato certo
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    views.forEach(function (v) {
      if (v._go && v._go(id)) setTimeout(function () { v.scrollIntoView({ block: 'start' }); }, 0);
    });
  }
  window.addEventListener('hashchange', fromHash);
  fromHash();
})();
/* botão "Copiar" dos regex de vendor */
document.addEventListener('click', function (ev) {
  var b = ev.target.closest && ev.target.closest('.rxcopy'); if (!b) return;
  var t = b.getAttribute('data-rx'), done = function () { b.textContent = 'Copiado'; setTimeout(function () { b.textContent = 'Copiar'; }, 2000); };
  if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () { window.prompt('Copie o regex:', t); });
  else window.prompt('Copie o regex:', t);
});
