// Site search. Loads one index of pages, glossary terms, organizations,
// cases, trials and papers, and filters it in the browser.
(function () {
  'use strict';
  var box = document.getElementById('q');
  var out = document.getElementById('search-results');
  var count = document.getElementById('search-count');
  if (!box || !out) return;
  var ORDER = ['Page', 'Section', 'Glossary', 'Organization', 'Trial', 'Case', 'Paper'];
  var PLURAL = { Page: 'Pages', Section: 'Sections', Glossary: 'Glossary', Organization: 'Organizations',
                 Trial: 'Trials', Case: 'Published cases', Paper: 'Papers' };
  var LIMIT = 40;
  var index = null;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }

  function run() {
    var words = box.value.toLowerCase().split(/\s+/).filter(Boolean);
    if (!index) return;
    if (!words.length) { out.innerHTML = ''; count.textContent = index.length.toLocaleString('en-US') + ' entries to search.'; return; }
    var groups = {}, total = 0;
    index.forEach(function (e) {
      var hay = e.hay;
      for (var i = 0; i < words.length; i++) { if (hay.indexOf(words[i]) < 0) return; }
      (groups[e.kind] = groups[e.kind] || []).push(e);
      total++;
    });
    var html = '';
    ORDER.forEach(function (kind) {
      var list = groups[kind];
      if (!list) return;
      html += '<div class="year-group"><h2>' + PLURAL[kind] + ' <small>' + list.length + '</small></h2>';
      list.slice(0, LIMIT).forEach(function (e) {
        var ext = /^https?:/.test(e.url);
        html += '<div class="paper"><div class="paper-title"><a href="' + esc(ext ? e.url : '../' + e.url) + '"'
          + (ext ? ' rel="noopener"' : '') + '>' + esc(e.title) + '</a></div>'
          + (e.sub ? '<div class="paper-meta">' + esc(e.sub) + '</div>' : '') + '</div>';
      });
      if (list.length > LIMIT) html += '<p class="fineprint">' + (list.length - LIMIT) + ' more. Add a word to narrow it down.</p>';
      html += '</div>';
    });
    out.innerHTML = html || '<p>Nothing matches. Try one word, or a year.</p>';
    count.textContent = total.toLocaleString('en-US') + ' results';
  }

  fetch('../data/search.json').then(function (r) { return r.json(); }).then(function (rows) {
    index = rows.map(function (r) {
      return { kind: r[0], title: r[1], sub: r[2], url: r[3], hay: (r[1] + ' ' + r[2] + ' ' + r[0]).toLowerCase() };
    });
    var q = new URLSearchParams(location.search).get('q');
    if (q) box.value = q;
    run();
  }).catch(function () { count.textContent = 'The search index could not be loaded.'; });

  var timer;
  box.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
})();
