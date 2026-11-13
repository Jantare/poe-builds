/* Links "Comprar" para o site de trade oficial. A busca fica em data-q; aqui juntamos com a liga escolhida.
   O nome da liga no trade só é confirmado quando a liga abre; dá para trocar no seletor (fica salvo neste navegador). */
(function () {
  var DEFAULT = 'Covens';
  var LEAGUES = [DEFAULT, 'Hardcore ' + DEFAULT, 'Standard', 'Hardcore'];
  var KEY = 'poebuilds.tradeLeague2';
  var links = document.querySelectorAll('a.buy[data-q]');
  var sels = document.querySelectorAll('select.tradelg');
  if (!links.length) return;
  var league = DEFAULT;
  try { league = localStorage.getItem(KEY) || DEFAULT; } catch (e) {}
  function apply() {
    [].forEach.call(links, function (a) {
      a.href = 'https://www.pathofexile.com/trade/search/' + encodeURIComponent(league) + '?q=' + encodeURIComponent(a.getAttribute('data-q'));
    });
    [].forEach.call(sels, function (s) {
      var opts = LEAGUES.indexOf(league) < 0 ? LEAGUES.concat([league]) : LEAGUES;
      s.innerHTML = opts.map(function (l) { return '<option' + (l === league ? ' selected' : '') + '>' + l.replace(/</g, '&lt;') + '</option>'; }).join('') + '<option value="__other">Outra liga…</option>';
    });
  }
  [].forEach.call(sels, function (s) {
    s.addEventListener('change', function () {
      var v = s.value;
      if (v === '__other') { v = (window.prompt('Nome da liga como aparece no site de trade:', league) || '').trim(); if (!v) { apply(); return; } }
      league = v;
      try { localStorage.setItem(KEY, league); } catch (e) {}
      apply();
    });
  });
  apply();
})();
