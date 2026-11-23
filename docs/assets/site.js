(function () {
  var root = document.documentElement;
  root.classList.add('js');

  // Menu téléphone
  var btn = document.querySelector('.menu-btn');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.querySelector('.lbl').textContent = open ? 'Fermer' : 'Menu';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('menu-open')) btn.click();
    });
  }

  // Apparition douce au défilement
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  // Filtres des réalisations
  var filters = document.querySelector('.filters');
  if (filters) {
    var cards = document.querySelectorAll('.gallery .card');
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      var f = b.getAttribute('data-filter');
      cards.forEach(function (c) {
        var show = f === 'tout' || c.getAttribute('data-cat') === f;
        c.hidden = !show;
        if (show) c.classList.add('is-in');
      });
    });
  }

  // Visionneuse des fiches projet
  var gal = document.querySelector('.proj-gallery');
  if (gal) {
    var shots = Array.prototype.slice.call(gal.querySelectorAll('button'));
    var lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Photo agrandie');
    lb.innerHTML = '<img alt=""><button class="lb-close" type="button">Fermer ✕</button>' +
      '<button class="lb-prev" type="button">← Préc.</button><button class="lb-next" type="button">Suiv. →</button>' +
      '<span class="lb-count"></span>';
    document.body.appendChild(lb);
    var img = lb.querySelector('img'), count = lb.querySelector('.lb-count'), cur = 0, last = null;
    function show(i) {
      cur = (i + shots.length) % shots.length;
      var s = shots[cur];
      img.src = s.getAttribute('data-full');
      img.alt = s.querySelector('img').alt;
      count.textContent = (cur + 1) + ' / ' + shots.length;
    }
    function close() { lb.classList.remove('is-open'); document.body.style.overflow = ''; if (last) last.focus(); }
    shots.forEach(function (s, i) {
      s.addEventListener('click', function () { last = s; show(i); lb.classList.add('is-open'); document.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); });
    });
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(cur - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(cur - 1);
      if (e.key === 'ArrowRight') show(cur + 1);
    });
  }

  // Formulaire de contact : ouvre la messagerie avec le message prérempli
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (n) { return (form.elements[n] && form.elements[n].value || '').trim(); };
      var subject = 'Demande de contact' + (v('projet') ? ' — ' + v('projet') : '');
      var body = v('message') + '\n\n' + v('nom') + (v('tel') ? '\n' + v('tel') : '') + (v('email') ? '\n' + v('email') : '') + (v('lieu') ? '\nLieu du projet : ' + v('lieu') : '');
      window.location.href = 'mailto:' + form.getAttribute('data-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    });
  }
})();
