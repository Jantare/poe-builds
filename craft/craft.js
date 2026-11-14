/* Simulador de craft (PoE 1). Monte Carlo com os pesos de mods do Path of Building. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var BASES = {}, MODS = {}, ESS = [];
  var state = { base: null, ilvl: 84, method: 'chaos', targets: [] };
  var cache = null; // pool for current base+ilvl

  // Presets: build links (base, ilvl, method, targets "group:tier")
  var PRESETS = [
    ['ES/CI · elmo Hubris', 'Hubris Circlet', 84, 'chaos', 'LocalEnergyShield:2,LocalEnergyShieldPercent:2'],
    ['ES/CI · Rune Dagger +1', 'Copper Kris', 84, 'chaos', 'GlobalIncreaseSpellSkillGemLevel:1'],
    ['ES/CI · luvas supressão', 'Murder Mitts', 84, 'chaos', 'ChanceToSuppressSpells:3,LocalEvasionAndEnergyShield:3'],
    ['ES/CI · botas', 'Murder Boots', 84, 'chaos', 'MovementVelocity:2,ChanceToSuppressSpells:3'],
    ['ED · Vaal Regalia', 'Vaal Regalia', 84, 'chaos', 'LocalEnergyShieldPercent:2,LocalEnergyShield:2'],
    ['Ballista · aljava', 'Artillery Quiver', 84, 'chaos', 'IncreasedLife:3'],
    ['Jewel de ES e crítico', 'Cobalt Jewel', 84, 'chaos', 'EnergyShieldForJewel:1,SpellCritMultiplierForJewel:1']
  ];

  function weightFor(mod, tags) {
    if (mod.j && !tags.jewel) return 0;
    if (!mod.j && tags.jewel) return 0;
    for (var i = 0; i < mod.wk.length; i++) if (tags[mod.wk[i]]) return mod.wv[i] || 0;
    return 0;
  }
  function maxAffix(base) { return base.type === 'Jewel' ? 2 : 3; }
  function fmt(n, d) { return Number(n).toLocaleString('pt-BR', { maximumFractionDigits: d == null ? 2 : d }); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function buildPool() {
    var b = BASES[state.base]; if (!b) { cache = null; return; }
    var tags = {}; b.tags.forEach(function (t) { tags[t] = true; });
    var all = [], groups = {};
    Object.keys(MODS).forEach(function (id) {
      var m = MODS[id], w = weightFor(m, tags);
      if (w <= 0) return;
      var g = groups[m.g] || (groups[m.g] = { g: m.g, t: m.t, tiers: [] });
      g.tiers.push({ id: id, l: m.l, w: w, x: m.x });
    });
    Object.keys(groups).forEach(function (k) {
      var g = groups[k];
      g.tiers.sort(function (a, b) { return b.l - a.l; });
      g.tiers.forEach(function (t, i) { t.tier = i + 1; });
      g.avail = g.tiers.filter(function (t) { return t.l <= state.ilvl; });
      g.w = g.avail.reduce(function (s, t) { return s + t.w; }, 0);
      g.avail.forEach(function (t) { all.push({ id: t.id, g: k, t: g.t, w: t.w, tier: t.tier, x: t.x }); });
    });
    var total = all.reduce(function (s, m) { return s + m.w; }, 0);
    cache = { base: b, all: all, groups: groups, total: total };
  }

  function pickWeighted(list, total) {
    var r = Math.random() * total;
    for (var i = 0; i < list.length; i++) { r -= list[i].w; if (r <= 0) return list[i]; }
    return list[list.length - 1];
  }
  function fill(item, count, maxP, maxS, onlySide) {
    var all = cache.all;
    while (item.length < count) {
      var used = {}, p = 0, s = 0;
      item.forEach(function (m) { used[m.g] = 1; if (m.t === 'P') p++; else s++; });
      var pool = [], tot = 0;
      for (var i = 0; i < all.length; i++) {
        var m = all[i];
        if (used[m.g]) continue;
        if (m.t === 'P' && (p >= maxP || onlySide === 'S')) continue;
        if (m.t === 'S' && (s >= maxS || onlySide === 'P')) continue;
        pool.push(m); tot += m.w;
      }
      if (!pool.length) break;
      item.push(pickWeighted(pool, tot));
    }
    return item;
  }
  function rareCount(base) {
    if (base.type === 'Jewel') return Math.random() < 0.5 ? 3 : 4;
    var r = Math.random() * 12; return r < 8 ? 4 : r < 11 ? 5 : 6;
  }
  function targetMod(t) {
    var g = cache.groups[t.g]; if (!g) return null;
    var tier = g.avail.filter(function (x) { return x.tier <= t.tier; })[0] || g.avail[0];
    return tier ? { id: tier.id, g: t.g, t: g.t, w: tier.w, tier: tier.tier, x: tier.x } : null;
  }
  function rollOnce() {
    var b = cache.base, max = maxAffix(b), item = [];
    switch (state.method) {
      case 'alt':
        return fill([], Math.random() < 0.5 ? 1 : 2, 1, 1);
      case 'essence':
        var em = essenceMod();
        if (em) item.push(em);
        return fill(item, rareCount(b), max, max);
      case 'lockP':
      case 'lockS':
        var side = state.method === 'lockP' ? 'P' : 'S', other = side === 'P' ? 'S' : 'P';
        state.targets.forEach(function (t) {
          var m = targetMod(t); if (m && m.t === side) item.push(m);
        });
        var n = item.length + 1 + Math.floor(Math.random() * max);
        return fill(item, n, side === 'P' ? item.length : max, side === 'S' ? item.length : max, other);
      default:
        return fill([], rareCount(b), max, max);
    }
  }
  function essenceMod() {
    var e = ESS[+$('essence').value]; if (!e) return null;
    var mid = e.m[cache.base.type]; if (!mid) return null;
    var m = MODS[mid], g = cache.groups[m.g];
    var tier = g ? (g.tiers.filter(function (t) { return t.id === mid; })[0] || {}).tier : 1;
    return { id: mid, g: m.g, t: m.t, w: 0, tier: tier || 1, x: m.x };
  }
  function success(item) {
    return state.targets.every(function (t) {
      return item.some(function (m) { return m.g === t.g && m.tier <= t.tier; });
    });
  }
  function costPerTry() {
    var c = +$('pChaos').value || 0, a = +$('pAlt').value || 0, e = +$('pEss').value || 0, d = +$('pDiv').value || 0;
    var locked = state.targets.filter(function (t) { var g = cache.groups[t.g]; return g && g.t === (state.method === 'lockP' ? 'P' : 'S'); }).length;
    switch (state.method) {
      case 'alt': return a;
      case 'essence': return e;
      case 'lockP': case 'lockS': return c + (locked <= 1 ? d : 2 * d);
      default: return c;
    }
  }

  function run() {
    if (!cache || !state.targets.length) { $('result').innerHTML = '<p class="muted">Escolha uma base e pelo menos um mod desejado.</p>'; return; }
    if (state.method === 'lockP' || state.method === 'lockS') {
      var side = state.method === 'lockP' ? 'P' : 'S';
      if (state.targets.every(function (t) { return cache.groups[t.g] && cache.groups[t.g].t === side; })) {
        $('result').innerHTML = '<p class="muted">Todos os mods marcados já estão travados. Marque também os mods que você quer do outro lado (' + (side === 'P' ? 'sufixos' : 'prefixos') + ').</p>'; return;
      }
    }
    $('run').disabled = true;
    var N = 0, hits = 0, sample = null, t0 = performance.now();
    (function chunk() {
      for (var i = 0; i < 4000; i++) {
        var it = rollOnce(); N++;
        if (success(it)) { hits++; if (!sample) sample = it; }
      }
      if (N < 200000 && performance.now() - t0 < 1500) return setTimeout(chunk, 0);
      $('run').disabled = false;
      var p = hits / N, cost = costPerTry();
      var html = '<div><span>Chance por tentativa</span><b>' + (p ? fmt(p * 100, p < 0.01 ? 3 : 2) + '%' : '< ' + fmt(100 / N, 4) + '%') + '</b></div>';
      html += '<div><span>Tentativas em média</span><b>' + (p ? fmt(1 / p, 0) : '—') + '</b></div>';
      html += '<div><span>Custo médio</span><b>' + (p ? fmt(cost / p, 0) + ' c' : '—') + '</b></div>';
      html += '<div><span>Custo por tentativa</span><b>' + fmt(cost, 2) + ' c</b></div>';
      html += '<div><span>Simulações</span><b>' + fmt(N, 0) + '</b></div>';
      $('result').innerHTML = html;
      if (!p) $('result').insertAdjacentHTML('beforeend', '<p class="muted" style="grid-column:1/-1">Nenhum acerto nas simulações. Tente outro método, menos mods ao mesmo tempo ou um tier mínimo mais baixo.</p>');
      $('sampleBox').hidden = !sample;
      if (sample) $('sample').textContent = sample.map(function (m) { return '[' + m.t + ' T' + m.tier + '] ' + m.x.join(' / '); }).join('\n');
      writeQuery();
    })();
  }

  function renderTypes() {
    var types = {};
    Object.keys(BASES).forEach(function (n) { types[BASES[n].type] = 1; });
    $('type').innerHTML = Object.keys(types).sort().map(function (t) { return '<option>' + esc(t) + '</option>'; }).join('');
  }
  function renderBases() {
    var type = $('type').value, f = $('baseSearch').value.toLowerCase();
    var list = Object.keys(BASES).filter(function (n) { return BASES[n].type === type && n.toLowerCase().indexOf(f) >= 0; })
      .sort(function (a, b) { return BASES[b].lvl - BASES[a].lvl || a.localeCompare(b); });
    $('base').innerHTML = list.map(function (n) {
      var b = BASES[n];
      return '<option value="' + esc(n) + '"' + (n === state.base ? ' selected' : '') + '>' + esc(n) + (b.sub ? ' · ' + esc(b.sub) : '') + ' (nv ' + b.lvl + ')</option>';
    }).join('');
    if (list.indexOf(state.base) < 0 && list.length) { state.base = list[0]; $('base').value = list[0]; }
  }
  function renderEssences() {
    var t = BASES[state.base] && BASES[state.base].type;
    $('essence').innerHTML = ESS.map(function (e, i) {
      var mid = e.m[t]; if (!mid) return '';
      return '<option value="' + i + '">' + esc(e.n) + ' → ' + esc(MODS[mid].x.join(' / ')) + '</option>';
    }).join('');
  }
  function renderMods() {
    if (!cache) return;
    var f = $('modSearch').value.toLowerCase(), side = $('modSide').value;
    var chosen = {}; state.targets.forEach(function (t) { chosen[t.g] = 1; });
    var gs = Object.keys(cache.groups).map(function (k) { return cache.groups[k]; })
      .filter(function (g) { return g.w > 0 && (!side || g.t === side); })
      .filter(function (g) { return !f || g.avail.some(function (t) { return t.x.join(' ').toLowerCase().indexOf(f) >= 0; }); })
      .sort(function (a, b) { return b.w - a.w; });
    var max = gs.length ? Math.max.apply(null, gs.map(function (g) { return g.w; })) : 1;
    $('mods').innerHTML = gs.map(function (g) {
      var best = g.avail[0], pct = g.w / cache.total * 100;
      return '<tr' + (chosen[g.g] ? ' class="on"' : '') + '><td>' + esc(best.x.join(' / ')) + '<div class="muted">' + g.avail.length + ' tiers neste item level</div></td>' +
        '<td><span class="ps ' + g.t + '">' + g.t + '</span></td>' +
        '<td><div class="bar"><i style="width:' + (g.w / max * 100).toFixed(1) + '%"></i></div><span class="muted">' + fmt(pct, 2) + '%</span></td>' +
        '<td><button type="button" data-g="' + esc(g.g) + '">' + (chosen[g.g] ? 'Remover' : 'Querer') + '</button></td></tr>';
    }).join('');
    $('poolInfo').textContent = gs.length + ' grupos de mods · chance = peso do grupo ÷ peso total, por sorteio de mod';
  }
  function renderTargets() {
    if (!state.targets.length) { $('targets').innerHTML = '<p class="muted">Clique em "Querer" na tabela para adicionar.</p>'; return; }
    $('targets').innerHTML = state.targets.map(function (t, i) {
      var g = cache && cache.groups[t.g];
      if (!g) return '';
      var opts = g.avail.map(function (x) { return '<option value="' + x.tier + '"' + (x.tier === t.tier ? ' selected' : '') + '>T' + x.tier + ' ou melhor: ' + esc(x.x.join(' / ')) + '</option>'; }).join('');
      return '<div class="tgt"><span class="ps ' + g.t + '">' + g.t + '</span><select data-i="' + i + '">' + opts + '</select><span></span><button type="button" aria-label="Remover" data-r="' + i + '">×</button></div>';
    }).join('');
  }
  function methodNote() {
    var notes = {
      chaos: 'Cada Chaos rerola o item raro inteiro (4 a 6 mods).',
      alt: 'Cada Alteration rerola o item mágico (1 prefixo e/ou 1 sufixo). Depois use Regal para virar raro.',
      essence: 'A essência garante um mod e sorteia o resto como um Chaos.',
      lockP: '3.30: os mods desejados que são prefixos ficam travados (1 Divine para 1 afixo, 2 para dois). O Chaos rerola só os sufixos.',
      lockS: '3.30: os mods desejados que são sufixos ficam travados. O Chaos rerola só os prefixos.'
    };
    $('methodNote').textContent = notes[state.method];
    $('essField').hidden = state.method !== 'essence';
  }
  function refresh() {
    state.ilvl = Math.max(1, Math.min(86, +$('ilvl').value || 84));
    buildPool(); renderEssences(); renderMods();
    state.targets = state.targets.filter(function (t) { return cache && cache.groups[t.g] && cache.groups[t.g].avail.length; });
    state.targets.forEach(function (t) { var g = cache.groups[t.g]; if (t.tier > g.avail[g.avail.length - 1].tier) t.tier = g.avail[g.avail.length - 1].tier; if (t.tier < g.avail[0].tier) t.tier = g.avail[0].tier; });
    renderTargets(); methodNote(); $('result').innerHTML = ''; $('sampleBox').hidden = true;
  }
  function writeQuery() {
    try {
      var q = new URLSearchParams({ base: state.base, ilvl: state.ilvl, m: state.method, t: state.targets.map(function (t) { return t.g + ':' + t.tier; }).join(',') });
      history.replaceState(null, '', '?' + q.toString());
    } catch (e) {}
  }
  function readQuery(q) {
    var p = new URLSearchParams(q);
    if (p.get('base') && BASES[p.get('base')]) { state.base = p.get('base'); $('type').value = BASES[state.base].type; }
    if (p.get('ilvl')) $('ilvl').value = p.get('ilvl');
    if (p.get('m')) { state.method = p.get('m'); $('method').value = state.method; }
    state.targets = (p.get('t') || '').split(',').filter(Boolean).map(function (s) { var a = s.split(':'); return { g: a[0], tier: +a[1] || 1 }; });
  }

  function bind() {
    $('type').addEventListener('change', function () { state.base = null; renderBases(); refresh(); });
    $('baseSearch').addEventListener('input', function () { renderBases(); refresh(); });
    $('base').addEventListener('change', function () { state.base = $('base').value; refresh(); });
    $('ilvl').addEventListener('change', refresh);
    $('method').addEventListener('change', function () { state.method = $('method').value; methodNote(); });
    $('modSearch').addEventListener('input', renderMods);
    $('modSide').addEventListener('change', renderMods);
    $('mods').addEventListener('click', function (e) {
      var g = e.target.getAttribute && e.target.getAttribute('data-g'); if (!g) return;
      var i = state.targets.findIndex(function (t) { return t.g === g; });
      if (i >= 0) state.targets.splice(i, 1); else state.targets.push({ g: g, tier: cache.groups[g].avail[0].tier });
      renderTargets(); renderMods();
    });
    $('targets').addEventListener('change', function (e) { var i = e.target.getAttribute('data-i'); if (i != null) state.targets[+i].tier = +e.target.value; });
    $('targets').addEventListener('click', function (e) { var i = e.target.getAttribute('data-r'); if (i != null) { state.targets.splice(+i, 1); renderTargets(); renderMods(); } });
    $('run').addEventListener('click', run);
  }

  Promise.all(['bases', 'mods', 'essences'].map(function (n) { return fetch('../data/craft/' + n + '.json').then(function (r) { return r.json(); }); }))
    .then(function (d) {
      BASES = d[0]; MODS = d[1]; ESS = d[2];
      $('presets').innerHTML = PRESETS.filter(function (p) { return BASES[p[1]]; }).map(function (p) {
        return '<a href="?' + new URLSearchParams({ base: p[1], ilvl: p[2], m: p[3], t: p[4] }).toString() + '">' + esc(p[0]) + '</a>';
      }).join('');
      renderTypes();
      $('type').value = 'Helmet'; state.base = 'Hubris Circlet';
      readQuery(location.search);
      renderBases(); bind(); refresh();
    })
    .catch(function () {
      $('poolInfo').textContent = 'Não consegui carregar os dados. Abra o site pelo endereço do GitHub Pages (o navegador bloqueia os dados quando o arquivo é aberto direto do computador).';
    });
})();
