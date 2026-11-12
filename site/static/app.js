// Small progressive enhancements. The page reads fine without this file.
(function () {
  'use strict';

  // The headline figures are static on purpose. A count-up animation can be
  // caught mid-flight by a crawler or a screenshot and show a wrong number.

  // Menus in the masthead: one open at a time, closed by a click elsewhere or Escape.
  var menus = document.querySelectorAll('.menu');
  menus.forEach(function (m) {
    m.addEventListener('toggle', function () {
      if (m.open) menus.forEach(function (other) { if (other !== m) other.open = false; });
    });
  });
  document.addEventListener('click', function (e) {
    menus.forEach(function (m) { if (m.open && !m.contains(e.target)) m.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') menus.forEach(function (m) { m.open = false; });
  });

  // Tables on narrow screens. A table whose cells hold sentences is marked so the stylesheet can set
  // each row out as a record, and each cell is given its column heading. Other tables keep their
  // grid: if one is wider than its space, its wrapper is marked so a note says it scrolls.
  var tables = document.querySelectorAll('table.data-table');
  tables.forEach(function (t) {
    if (t.closest('.table-view')) return;
    var heads = Array.prototype.map.call(t.querySelectorAll('thead th'), function (th) { return th.textContent.trim(); });
    if (heads.length < 3) return;
    var rows = Array.prototype.slice.call(t.querySelectorAll('tbody tr'));
    var wordy = rows.slice(0, 20).some(function (tr) {
      return Array.prototype.some.call(tr.children, function (c) { return c.textContent.trim().length > 60; });
    });
    if (!wordy) return;
    t.classList.add('stack');
    rows.forEach(function (tr) {
      Array.prototype.forEach.call(tr.children, function (cell, i) { if (i > 0 && heads[i]) cell.setAttribute('data-label', heads[i]); });
    });
  });
  function markScrolling() {
    document.querySelectorAll('.table-wrap').forEach(function (w) {
      w.classList.toggle('scrolls', w.scrollWidth > w.clientWidth + 1);
    });
  }
  markScrolling();
  window.addEventListener('resize', markScrolling);

  // Mark the section being read in the contents column.
  var tocLinks = document.querySelectorAll('.sidebar .toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove('current'); });
        var link = byId[e.target.id];
        if (link) link.classList.add('current');
      });
    }, { rootMargin: '0px 0px -75% 0px' });
    document.querySelectorAll('.content > .section[id]').forEach(function (s) { spy.observe(s); });
  }

  // Tooltip for the column chart.
  document.querySelectorAll('.chart').forEach(function (chart) {
    var tip = chart.querySelector('.tooltip');
    if (!tip) return;
    chart.querySelectorAll('.hit').forEach(function (hit) {
      function show() {
        var box = chart.getBoundingClientRect(), r = hit.getBoundingClientRect();
        var top = parseFloat(hit.dataset.top);
        var svg = chart.querySelector('svg').getBoundingClientRect();
        var scale = svg.height / parseFloat(chart.dataset.h);
        tip.textContent = hit.dataset.tip;
        tip.style.left = (r.left + r.width / 2 - box.left) + 'px';
        tip.style.top = (svg.top - box.top + top * scale) + 'px';
        tip.classList.add('on');
      }
      function hide() { tip.classList.remove('on'); }
      hit.addEventListener('mouseenter', show);
      hit.addEventListener('focus', show);
      hit.addEventListener('mouseleave', hide);
      hit.addEventListener('blur', hide);
    });
  });

  // Directory filters.
  var dir = document.getElementById('directory-list');
  if (dir) {
    var search = document.getElementById('dir-search');
    var count = document.getElementById('dir-count');
    var papers = Array.prototype.slice.call(dir.querySelectorAll('.paper'));
    var groups = Array.prototype.slice.call(dir.querySelectorAll('.year-group'));
    var state = { site: 'all', kind: 'all', q: '' };
    var total = papers.length;
    var noun = dir.dataset.noun || 'papers';

    function apply() {
      var q = state.q.trim().toLowerCase(), shown = 0;
      papers.forEach(function (p) {
        var ok = (state.site === 'all' || (' ' + p.dataset.sites + ' ').indexOf(' ' + state.site + ' ') >= 0)
          && (state.kind === 'all' || (' ' + p.dataset.kind + ' ').indexOf(' ' + state.kind + ' ') >= 0)
          && (!q || p.dataset.text.indexOf(q) >= 0);
        p.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) {
        var n = g.querySelectorAll('.paper:not([hidden])').length;
        g.hidden = n === 0;
        var small = g.querySelector('h2 small');
        if (small) small.textContent = n + ' ' + (n === 1 ? noun.replace(/s$/, '') : noun);
      });
      count.textContent = shown.toLocaleString('en-US') + ' of ' + total.toLocaleString('en-US') + ' ' + noun + ' shown';
    }

    function press(group, value) {
      state[group] = value;
      document.querySelectorAll('.filter-btn[data-group="' + group + '"]').forEach(function (b) {
        b.setAttribute('aria-pressed', b.dataset.value === value ? 'true' : 'false');
      });
      apply();
    }

    document.querySelectorAll('.filter-btn').forEach(function (b) {
      b.addEventListener('click', function () { press(b.dataset.group, b.dataset.value); });
    });
    var timer;
    search.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { state.q = search.value; apply(); }, 120);
    });

    // Links such as papers/#skin open with that filter on.
    var hash = location.hash.replace('#', '');
    if (hash && document.querySelector('.filter-btn[data-group="site"][data-value="' + hash + '"]')) {
      press('site', hash);
    } else if (hash === 'focus' && document.querySelector('.filter-btn[data-value="focus"]')) {
      press('kind', 'focus');
    } else {
      apply();
    }
  }
})();
