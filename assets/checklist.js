(function () {
  var s = document.currentScript, KEY = (s && s.getAttribute('data-key')) || 'checks';
  var boxes = [].slice.call(document.querySelectorAll('#acts input[type=checkbox]'));
  if (!boxes.length) return;
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) {}
  function update() {
    var done = boxes.filter(function (b) { return b.checked; }).length;
    var c = document.getElementById('count'), bar = document.getElementById('bar');
    if (c) c.textContent = done + ' de ' + boxes.length;
    if (bar) bar.style.width = (done / boxes.length * 100) + '%';
  }
  function save() {
    var o = {}; boxes.forEach(function (b) { if (b.checked) o[b.id] = 1; });
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {}
  }
  boxes.forEach(function (b) { b.checked = !!saved[b.id]; b.addEventListener('change', function () { save(); update(); }); });
  var r = document.getElementById('reset');
  if (r) r.addEventListener('click', function () { boxes.forEach(function (b) { b.checked = false; }); save(); update(); });
  update();
})();
