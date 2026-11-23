(function () {
  'use strict';
  var doc = document, body = doc.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var hasGsap = !!(window.gsap && window.ScrollTrigger) && !reduce;
  var bars = $('.bars');

  /* ---------- Ouverture (accueil, une fois par visite) et entrée des pages ---------- */
  var isHome = body.classList.contains('home');
  var seen = false;
  try { seen = sessionStorage.getItem('a4f-intro') === '1'; } catch (e) {}
  var skip = $('.intro-skip');
  function open() { bars.classList.remove('is-credit'); bars.classList.add('is-open'); body.classList.add('ready'); if (skip) skip.hidden = true; }
  if (reduce) { body.classList.add('ready'); }
  else if (isHome && !seen) {
    try { sessionStorage.setItem('a4f-intro', '1'); } catch (e) {}
    if (skip) { skip.hidden = false; skip.addEventListener('click', open); }
    setTimeout(function () { bars.classList.add('is-credit'); }, 200);
    setTimeout(open, 2300);
  } else {
    requestAnimationFrame(function () { setTimeout(open, 60); });
  }

  /* ---------- Transition entre les pages : les bandes se referment ---------- */
  if (!reduce) {
    doc.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto|tel|https?):/.test(href)) return;
      e.preventDefault();
      body.classList.add('leaving');
      setTimeout(function () { location.href = href; }, 560);
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) { body.classList.remove('leaving'); open(); } });
  }

  /* ---------- Barre du haut masquée en descendant ---------- */
  var top = $('.top'), lastY = 0;
  window.addEventListener('scroll', function () {
    var y = window.scrollY;
    if (!body.classList.contains('menu-open')) top.classList.toggle('is-hidden', y > 300 && y > lastY + 3);
    if (y < lastY - 3) top.classList.remove('is-hidden');
    lastY = y;
  }, { passive: true });

  /* ---------- Menu ---------- */
  var mbtn = $('.menu-btn'), lenis = null;
  if (mbtn) {
    mbtn.addEventListener('click', function () {
      var o = body.classList.toggle('menu-open');
      mbtn.setAttribute('aria-expanded', o ? 'true' : 'false');
      mbtn.textContent = o ? 'Fermer' : 'Menu';
      if (lenis) o ? lenis.stop() : lenis.start();
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && body.classList.contains('menu-open')) mbtn.click(); });
  }

  /* ---------- Apparitions ---------- */
  var obs = $$('.rv, .tl');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { threshold: .15 });
    obs.forEach(function (el) { io.observe(el); });
  } else obs.forEach(function (el) { el.classList.add('in'); });

  /* ---------- Citation mot à mot ---------- */
  $$('[data-words]').forEach(function (q) {
    q.innerHTML = q.textContent.trim().split(/\s+/).map(function (w) { return '<span class="qw">' + w + '</span>'; }).join(' ');
  });

  if (hasGsap) {
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      lenis = new Lenis({ lerp: .08 });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }

    /* Plan d’ouverture : le titre recule au défilement */
    $$('.shot').forEach(function (s) {
      var t = $('.title', s);
      if (t) gsap.to(t, { yPercent: -35, opacity: 0, ease: 'none', scrollTrigger: { trigger: s, start: 'top top', end: 'bottom top', scrub: true } });
    });

    /* Scènes épinglées */
    $$('.story').forEach(function (story) {
      var scenes = $$('.scene', story), subs = $$('.sub', story), counter = $('.counter', story), prog = $('.progress i', story), fig = $('.bigfig', story);
      var n = scenes.length;
      var tl = gsap.timeline({ scrollTrigger: { trigger: story, start: 'top top', end: '+=' + (n * 100) + '%', pin: $('.stage', story), scrub: .8,
        onUpdate: function (st) {
          if (prog) prog.style.transform = 'scaleX(' + st.progress + ')';
          if (counter) counter.textContent = ('0' + Math.min(n, Math.floor(st.progress * n) + 1)).slice(-2) + ' / ' + ('0' + n).slice(-2);
        } } });
      scenes.forEach(function (s, i) {
        tl.fromTo($('img', s), { scale: 1.22 }, { scale: 1.02, ease: 'none', duration: 1.2 }, i === 0 ? 0 : i - .2);
        var txt = $('.txt', s);
        if (i > 0) {
          tl.fromTo(s, { clipPath: 'inset(0% 0% 0% 100%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'power3.inOut', duration: .6 }, i - .2);
          if (subs[i - 1]) tl.to(subs[i - 1], { opacity: 0, y: -12, duration: .2 }, i - .25);
          if (subs[i]) tl.fromTo(subs[i], { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .25 }, i + .15);
        }
        if (txt) tl.fromTo(txt, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .3 }, i === 0 ? 0 : i + .1);
      });
      if (fig) tl.to(fig, { opacity: 1, duration: .3 }, n - .6);
      tl.to({}, { duration: .4 });
    });

    /* Fondus de couleur */
    $$('.colors').forEach(function (c) {
      var words = $$('.cword', c), stage = $('.cstage', c);
      var cols = (c.getAttribute('data-colors') || '#dde3cf/#22301e,#7d8a3c/#f6f1e3,#d99a3d/#22301e,#3f5a34/#f6f1e3').split(',').map(function (x) { return x.split('/'); });
      var ct = gsap.timeline({ scrollTrigger: { trigger: c, start: 'top top', end: '+=' + (words.length * 80) + '%', pin: stage, scrub: .6 } });
      words.forEach(function (w, i) {
        ct.fromTo($('h2', w), { scale: .86 }, { scale: 1, duration: 1, ease: 'none' }, i);
        if (i > 0) ct.to(words[i - 1], { opacity: 0, y: -40, duration: .3 }, i - .15)
          .to(stage, { backgroundColor: cols[i % cols.length][0], color: cols[i % cols.length][1], duration: .35 }, i - .15)
          .fromTo(w, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .3 }, i);
      });
    });

    /* Pellicule horizontale (bureau) */
    ScrollTrigger.matchMedia({ '(min-width: 761px)': function () {
      $$('.film').forEach(function (f) {
        var reel = $('.reel', f);
        if (!reel) return;
        gsap.to(reel, { x: function () { return -Math.max(0, reel.scrollWidth - innerWidth + 96); }, ease: 'none',
          scrollTrigger: { trigger: f, start: 'top top', end: function () { return '+=' + Math.max(1, reel.scrollWidth - innerWidth); }, pin: true, scrub: .8, invalidateOnRefresh: true } });
      });
    } });

    /* Parallaxe des arrière-plans */
    $$('.quote .bg, .next .bg').forEach(function (bg) {
      gsap.fromTo(bg, { yPercent: -5 }, { yPercent: 5, ease: 'none', scrollTrigger: { trigger: bg.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
    $$('.quote').forEach(function (q) {
      var ws = $$('.qw', q);
      if (ws.length) gsap.to(ws, { opacity: 1, stagger: .1, ease: 'none', scrollTrigger: { trigger: $('blockquote', q), start: 'top 80%', end: 'bottom 40%', scrub: true } });
    });

    /* Frise */
    $$('.timeline').forEach(function (t) {
      var bar = $('.bar', t);
      ScrollTrigger.create({ trigger: t, start: 'top 70%', end: 'bottom 60%', scrub: true, onUpdate: function (st) { bar.style.height = (st.progress * (t.offsetHeight - 12)) + 'px'; } });
    });
  } else {
    $$('.quote .qw').forEach(function (w) { w.style.opacity = 1; });
    $$('.timeline .bar').forEach(function (b) { b.style.height = 'calc(100% - 12px)'; });
  }

  /* ---------- Filtres de la filmographie ---------- */
  var filters = $('.filters');
  if (filters) {
    var tiles = $$('.frames .tile');
    var apply = function (f, push) {
      $$('button', filters).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-filter') === f ? 'true' : 'false'); });
      tiles.forEach(function (t) {
        var show = f === 'tout' || t.getAttribute('data-cat') === f;
        t.classList.toggle('is-hidden', !show);
        t.classList.remove('is-entering');
        if (show && !reduce) { void t.offsetWidth; t.classList.add('is-entering'); }
        if (show) t.classList.add('in');
      });
      var live = $('.filter-live'); if (live) live.textContent = tiles.filter(function (t) { return !t.classList.contains('is-hidden'); }).length + ' projet(s) affiché(s)';
      if (push) history.replaceState(null, '', f === 'tout' ? location.pathname : '#' + encodeURIComponent(f));
      if (hasGsap) ScrollTrigger.refresh();
    };
    filters.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) apply(b.getAttribute('data-filter'), true); });
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && $('[data-filter="' + h + '"]', filters)) apply(h, false);
  }

  /* ---------- Chiffres ---------- */
  $$('.bigfig [data-to], .count [data-to]').forEach(function (el) {
    var to = parseFloat(el.getAttribute('data-to')), pre = el.getAttribute('data-pre') || '';
    el.textContent = pre + to;
  });

  /* ---------- Visionneuse (photos d’un projet) ---------- */
  var shots = $$('button.frame');
  if (shots.length) {
    var lb = doc.createElement('div');
    lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo agrandie');
    lb.innerHTML = '<img alt=""><button class="lb-close mono" type="button">Fermer ✕</button><button class="lb-prev mono" type="button">← Préc.</button><button class="lb-next mono" type="button">Suiv. →</button><span class="lb-count mono"></span>';
    body.appendChild(lb);
    var img = $('img', lb), cnt = $('.lb-count', lb), cur = 0, last = null;
    var show = function (i) {
      cur = (i + shots.length) % shots.length;
      img.classList.add('is-swapping');
      var nimg = new Image();
      nimg.onload = function () { img.src = nimg.src; img.alt = $('img', shots[cur]).alt; img.classList.remove('is-swapping'); };
      nimg.src = shots[cur].getAttribute('data-full');
      cnt.textContent = (cur + 1) + ' / ' + shots.length;
    };
    var openLb = function (i, from) { last = from; show(i); lb.classList.add('is-open'); if (lenis) lenis.stop(); $('.lb-close', lb).focus(); };
    var shut = function () { lb.classList.remove('is-open'); if (lenis) lenis.start(); if (last) last.focus(); };
    shots.forEach(function (s, i) { s.addEventListener('click', function () { openLb(i, s); }); });
    $('.lb-close', lb).addEventListener('click', shut);
    $('.lb-prev', lb).addEventListener('click', function () { show(cur - 1); });
    $('.lb-next', lb).addEventListener('click', function () { show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) shut(); });
    doc.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') shut(); if (e.key === 'ArrowLeft') show(cur - 1); if (e.key === 'ArrowRight') show(cur + 1);
    });
    var x0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1)); x0 = null; });
  }

  /* ---------- Formulaire ---------- */
  var form = $('#contact-form');
  if (form) {
    var check = function (f) { var el = $('input, textarea, select', f); var ok = el.checkValidity(); f.classList.toggle('is-bad', !ok); return ok; };
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
      location.href = 'mailto:' + form.getAttribute('data-mail') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      var done = $('.sent', form); if (done) done.hidden = false;
    });
  }

  /* ---------- Touches de vie ---------- */
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // Heure de Vienne dans le pied de page
  var clock = $('[data-clock]');
  if (clock) {
    var tick = function () { try { clock.textContent = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris' }).format(new Date()); } catch (e) {} };
    tick(); setInterval(tick, 30000);
  }

  // Liane qui pousse quand on arrive en bas
  $$('.vine').forEach(function (v) {
    if (reduce || !('IntersectionObserver' in window)) { v.classList.add('grow'); return; }
    var vo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { v.classList.add('grow'); vo.disconnect(); } }, { threshold: .3 });
    vo.observe(v.parentElement);
  });

  // Titres qui montent mot à mot
  $$('.h2, .film h2, .fin').forEach(function (h) {
    if (reduce) return;
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = doc.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(doc.createTextNode(part)); return; }
            var w = doc.createElement('span'); w.className = 'wd';
            var inner = doc.createElement('span'); inner.textContent = part; inner.style.setProperty('--wd', (i++ * 0.06) + 's');
            w.appendChild(inner); frag.appendChild(w);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1 && c.tagName !== 'BR') walk(c);
      });
    })(h);
    var wo = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { h.classList.add('words-in'); wo.disconnect(); } }, { threshold: .4 });
    wo.observe(h);
  });

  if (fine && !reduce) {
    // Curseur
    var cur = $('.cursor'), cl = cur && $('span', cur), cx = innerWidth / 2, cy = innerHeight / 2, tx = cx, ty = cy;
    if (cur) {
      window.addEventListener('mousemove', function (e) { tx = e.clientX; ty = e.clientY; cur.classList.add('on'); }, { passive: true });
      doc.addEventListener('mouseleave', function () { cur.classList.remove('on'); });
      (function loop() { cx += (tx - cx) * .22; cy += (ty - cy) * .22; cur.style.transform = 'translate(' + cx + 'px,' + cy + 'px)'; requestAnimationFrame(loop); })();
      doc.addEventListener('mouseover', function (e) {
        var lab = e.target.closest('[data-cursor], .tile, a.frame, button.frame, .next');
        var hov = e.target.closest('a, button, summary, input, textarea, select');
        cur.classList.toggle('label', !!lab);
        cur.classList.toggle('hover', !lab && !!hov);
        if (lab) cl.textContent = lab.getAttribute('data-cursor') || (lab.tagName === 'BUTTON' ? 'Agrandir' : 'Voir');
      });
    }
    // Photos d’ouverture et pied de page qui suivent doucement la souris
    $$('.shot, .sf-scene').forEach(function (sec) {
      var bg = $('.bg, .sf-bg', sec);
      if (!bg) return;
      sec.addEventListener('mousemove', function (e) {
        var r = sec.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        bg.style.translate = (-x * 22).toFixed(1) + 'px ' + (-y * 16).toFixed(1) + 'px';
      });
      sec.addEventListener('mouseleave', function () { bg.style.translate = '0 0'; });
    });
    // Boutons aimantés
    $$('.btn, .sf-mail').forEach(function (b) {
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.translate = ((e.clientX - r.left - r.width / 2) * .18).toFixed(1) + 'px ' + ((e.clientY - r.top - r.height / 2) * .3).toFixed(1) + 'px';
      });
      b.addEventListener('mouseleave', function () { b.style.translate = '0 0'; });
    });
    // Vignettes qui s’inclinent légèrement
    $$('.tile .ph, .frame .ph').forEach(function (ph) {
      ph.addEventListener('mousemove', function (e) {
        var r = ph.getBoundingClientRect();
        ph.style.setProperty('--ry', (((e.clientX - r.left) / r.width - .5) * 6).toFixed(2) + 'deg');
        ph.style.setProperty('--rx', (-((e.clientY - r.top) / r.height - .5) * 6).toFixed(2) + 'deg');
      });
      ph.addEventListener('mouseleave', function () { ph.style.setProperty('--rx', '0deg'); ph.style.setProperty('--ry', '0deg'); });
    });
  }

  /* ---------- Panneaux des principes ---------- */
  $$('.panels').forEach(function (group) {
    var ps = $$('.panel', group);
    var openP = function (p) { ps.forEach(function (x) { x.classList.toggle('is-open', x === p); }); };
    ps.forEach(function (p) {
      p.addEventListener('mouseenter', function () { if (fine) openP(p); });
      p.addEventListener('focus', function () { openP(p); });
      p.addEventListener('click', function () { openP(p); });
      p.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openP(p); } });
    });
  });

  /* ---------- Haut de page ---------- */
  var tt = $('.to-top');
  if (tt) tt.addEventListener('click', function () { if (lenis) lenis.scrollTo(0, { duration: 1.4 }); else window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });

  window.addEventListener('load', function () { if (hasGsap) ScrollTrigger.refresh(); });
})();
