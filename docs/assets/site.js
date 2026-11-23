(function () {
  'use strict';
  var doc = document, body = doc.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  /* En-tête qui se resserre au défilement */
  var header = $('.site-header');
  var onScroll = function () { header.classList.toggle('is-scrolled', window.scrollY > 10); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Menu téléphone */
  var mbtn = $('.menu-btn');
  if (mbtn) {
    var close = function () { body.classList.remove('menu-open'); mbtn.setAttribute('aria-expanded', 'false'); $('.lbl', mbtn).textContent = 'Menu'; };
    mbtn.addEventListener('click', function () {
      var open = body.classList.toggle('menu-open');
      mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      $('.lbl', mbtn).textContent = open ? 'Fermer' : 'Menu';
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    window.addEventListener('resize', function () { if (window.innerWidth > 860) close(); });
  }

  /* Apparitions au défilement */
  var targets = $$('.rv, .rv-group, .hero, .tl');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el) { io.observe(el); });
  } else targets.forEach(function (el) { el.classList.add('is-in'); });

  /* Frise : la ligne se remplit au fil de la lecture */
  $$('.timeline').forEach(function (t) {
    var bar = $('.bar', t);
    if (!bar) return;
    var update = function () {
      var r = t.getBoundingClientRect(), vh = window.innerHeight;
      var p = Math.min(1, Math.max(0, (vh * 0.7 - r.top) / r.height));
      bar.style.height = (p * (r.height - 12)) + 'px';
    };
    if (reduce) { bar.style.height = 'calc(100% - 12px)'; return; }
    window.addEventListener('scroll', update, { passive: true });
    update();
  });

  /* Chiffres qui défilent */
  $$('.fig [data-to]').forEach(function (el) {
    var to = parseFloat(el.getAttribute('data-to')), pre = el.getAttribute('data-pre') || '';
    var show = function (v) { el.textContent = pre + Math.round(v); };
    if (reduce || !('IntersectionObserver' in window)) { show(to); return; }
    show(0);
    var o = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      o.disconnect();
      var t0 = performance.now();
      (function step(t) { var k = Math.min(1, (t - t0) / 1500); show(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); })(t0);
    }, { threshold: 0.5 });
    o.observe(el);
  });

  /* Filtres des réalisations (avec mémoire dans l’adresse) */
  var filters = $('.filters');
  if (filters) {
    var tiles = $$('.grid .tile');
    var apply = function (f, push) {
      $$('button', filters).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-filter') === f ? 'true' : 'false'); });
      tiles.forEach(function (t) {
        var show = f === 'tout' || t.getAttribute('data-cat') === f;
        var was = !t.classList.contains('is-hidden');
        t.classList.toggle('is-hidden', !show);
        t.classList.remove('is-entering');
        if (show && !reduce) { void t.offsetWidth; t.classList.add('is-entering'); }
        if (show && !was) t.classList.add('is-in');
      });
      var live = $('.filter-live');
      if (live) live.textContent = tiles.filter(function (t) { return !t.classList.contains('is-hidden'); }).length + ' réalisation(s) affichée(s)';
      if (push) history.replaceState(null, '', f === 'tout' ? location.pathname : '#' + encodeURIComponent(f));
    };
    filters.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) apply(b.getAttribute('data-filter'), true); });
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && $('[data-filter="' + h + '"]', filters)) apply(h, false);
  }

  /* Visionneuse des photos d’un projet (clavier, glisser au doigt) */
  var gal = $('.gal');
  if (gal) {
    var shots = $$('button', gal);
    var lb = doc.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo agrandie');
    lb.innerHTML = '<img alt=""><button class="lb-close" type="button">Fermer ✕</button><button class="lb-prev" type="button" aria-label="Photo précédente">←</button><button class="lb-next" type="button" aria-label="Photo suivante">→</button><span class="lb-count"></span>';
    body.appendChild(lb);
    var img = $('img', lb), count = $('.lb-count', lb), cur = 0, last = null;
    var show = function (i) {
      cur = (i + shots.length) % shots.length;
      var s = shots[cur];
      img.classList.add('is-swapping');
      var n = new Image();
      n.onload = function () { img.src = n.src; img.alt = $('img', s).alt; img.classList.remove('is-swapping'); };
      n.src = s.getAttribute('data-full');
      count.textContent = (cur + 1) + ' / ' + shots.length;
      var pre = new Image(); pre.src = shots[(cur + 1) % shots.length].getAttribute('data-full');
    };
    var open = function (i, from) { last = from; show(i); lb.classList.add('is-open'); body.style.overflow = 'hidden'; $('.lb-close', lb).focus(); };
    var shut = function () { lb.classList.remove('is-open'); body.style.overflow = ''; if (last) last.focus(); };
    shots.forEach(function (s, i) { s.addEventListener('click', function () { open(i, s); }); });
    $('.lb-close', lb).addEventListener('click', shut);
    $('.lb-prev', lb).addEventListener('click', function () { show(cur - 1); });
    $('.lb-next', lb).addEventListener('click', function () { show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) shut(); });
    doc.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') shut();
      if (e.key === 'ArrowLeft') show(cur - 1);
      if (e.key === 'ArrowRight') show(cur + 1);
    });
    var x0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }

  /* Formulaire : vérification douce, puis ouverture de la messagerie */
  var form = $('#contact-form');
  if (form) {
    var check = function (f) {
      var el = $('input, textarea, select', f);
      var ok = el.checkValidity();
      f.classList.toggle('is-bad', !ok);
      return ok;
    };
    $$('.field', form).forEach(function (f) {
      var el = $('input, textarea, select', f);
      el.addEventListener('blur', function () { if (el.value) check(f); });
      el.addEventListener('input', function () { if (f.classList.contains('is-bad')) check(f); });
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = $$('.field', form).filter(function (f) { return !check(f); });
      if (bad.length) { $('input, textarea', bad[0]).focus(); return; }
      var v = function (n) { return ((form.elements[n] && form.elements[n].value) || '').trim(); };
      var subject = 'Demande de contact' + (v('projet') ? ' — ' + v('projet') : '');
      var text = v('message') + '\n\n' + v('nom') + (v('tel') ? '\n' + v('tel') : '') + (v('email') ? '\n' + v('email') : '') + (v('lieu') ? '\nLieu du projet : ' + v('lieu') : '');
      window.location.href = 'mailto:' + form.getAttribute('data-mail') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      var done = $('.sent', form); if (done) done.hidden = false;
    });
  }
})();
