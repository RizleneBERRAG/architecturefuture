(function () {
  'use strict';
  var doc = document, body = doc.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var hasGsap = !!(window.gsap && window.ScrollTrigger) && !reduce;
  var lenis = null;

  /* ---------- Découpe des titres en lettres (sans couper les mots) ---------- */
  function splitChars(el) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = doc.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(doc.createTextNode(' ')); return; }
            var w = doc.createElement('span'); w.className = 'w';
            Array.prototype.forEach.call(part, function (ch) {
              var s = doc.createElement('span'); s.className = /[’']/.test(ch) ? 'ch ap' : 'ch'; s.textContent = ch;
              s.style.transitionDelay = (i++ * 0.028).toFixed(3) + 's';
              w.appendChild(s);
            });
            frag.appendChild(w);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1 && c.tagName !== 'BR') walk(c);
      });
    })(el);
    return i;
  }
  $$('[data-chars]').forEach(function (el) {
    var n = splitChars(el);
    $$('.ch', el).forEach(function (s, k) { s.style.transitionDelay = (0.35 + k * 0.05).toFixed(2) + 's'; });
  });
  $$('[data-type]').forEach(splitChars);

  /* ---------- Ouverture : voile avec le nom, une fois par visite ---------- */
  var seen = false;
  try { seen = sessionStorage.getItem('a4f-intro') === '1'; } catch (e) {}
  function ready() { body.classList.add('ready'); body.classList.remove('intro'); }
  if (reduce) ready();
  else if (body.classList.contains('home') && !seen) {
    try { sessionStorage.setItem('a4f-intro', '1'); } catch (e) {}
    body.classList.add('intro');
    setTimeout(ready, 1500);
  } else requestAnimationFrame(function () { setTimeout(ready, 40); });

  /* ---------- Transition entre les pages ---------- */
  if (!reduce) {
    doc.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto|tel|https?):/.test(href)) return;
      e.preventDefault();
      body.classList.add('leaving');
      setTimeout(function () { location.href = href; }, 520);
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) { body.classList.remove('leaving'); ready(); } });
  }

  /* ---------- En-tête : transparent sur la photo, blanc ensuite, masqué en descendant ---------- */
  var top = $('.top'), lastY = 0;
  var onScroll = function () {
    var y = window.scrollY || 0;
    top.classList.toggle('solid', y > 40 || !body.classList.contains('has-hero'));
    if (!body.classList.contains('menu-open')) {
      if (y > 500 && y > lastY + 4) top.classList.add('is-hidden');
      if (y < lastY - 4 || y < 200) top.classList.remove('is-hidden');
    }
    lastY = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Menu (téléphone) ---------- */
  var mbtn = $('.menu-btn');
  if (mbtn) {
    mbtn.addEventListener('click', function () {
      var o = body.classList.toggle('menu-open');
      mbtn.setAttribute('aria-expanded', o ? 'true' : 'false');
      $('span', mbtn).textContent = o ? 'Fermer' : 'Menu';
      if (lenis) o ? lenis.stop() : lenis.start();
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && body.classList.contains('menu-open')) mbtn.click(); });
  }

  /* ---------- Apparitions ---------- */
  var watch = $$('.rv, .rv-clip, .tile, .shot');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        if (e.target.hasAttribute('data-type')) e.target.classList.add('typed');
        io.unobserve(e.target);
      });
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    watch.forEach(function (el) { io.observe(el); });
    $$('[data-type]').forEach(function (el) { if (!el.classList.contains('rv')) io.observe(el); });
  } else {
    watch.forEach(function (el) { el.classList.add('in'); });
    $$('[data-type]').forEach(function (el) { el.classList.add('typed'); });
  }

  /* ---------- Diaporama d’ouverture ---------- */
  $$('.hero').forEach(function (h) {
    var slides = $$('.slide', h), cap = $('[data-cap-out]', h), cnt = $('[data-count]', h), prog = $('.hero-prog i', h);
    if (slides.length < 2) return;
    var k = 0, dur = 6500;
    var runProg = function () {
      if (!prog) return;
      prog.style.transition = 'none'; prog.style.transform = 'scaleX(0)';
      void prog.offsetWidth;
      prog.style.transition = 'transform ' + dur + 'ms linear'; prog.style.transform = 'scaleX(1)';
    };
    var go = function (n) {
      slides[k].classList.remove('is-on');
      k = (n + slides.length) % slides.length;
      slides[k].classList.add('is-on');
      if (cnt) cnt.textContent = ('0' + (k + 1)).slice(-2);
      if (cap) { cap.style.opacity = 0; setTimeout(function () { cap.textContent = slides[k].getAttribute('data-cap'); cap.style.opacity = 1; }, 500); }
      runProg();
    };
    if (reduce) return;
    runProg();
    setInterval(function () { if (!doc.hidden) go(k + 1); }, dur);
  });

  /* ---------- Citation mot à mot ---------- */
  $$('[data-words]').forEach(function (q) {
    q.innerHTML = q.textContent.trim().split(/\s+/).map(function (w) { return '<span class="qw">' + w + '</span>'; }).join(' ');
  });

  if (hasGsap) {
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      lenis = new Lenis({ lerp: .085 });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }

    /* Le titre d’ouverture s’éloigne doucement */
    $$('.hero').forEach(function (h) {
      gsap.to($('.hero-title', h), { yPercent: -28, opacity: 0, ease: 'none', scrollTrigger: { trigger: h, start: 'top top', end: 'bottom top', scrub: true } });
      gsap.to($('.slides', h), { yPercent: 14, ease: 'none', scrollTrigger: { trigger: h, start: 'top top', end: 'bottom top', scrub: true } });
    });

    /* Cercle qui dérive */
    $$('.ring').forEach(function (r) {
      gsap.fromTo(r, { y: 60 }, { y: -90, ease: 'none', scrollTrigger: { trigger: r.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* Citations : photo en parallaxe, mots qui s’allument */
    $$('.quote').forEach(function (q) {
      gsap.fromTo($('.q-bg', q), { yPercent: -6 }, { yPercent: 6, ease: 'none', scrollTrigger: { trigger: q, start: 'top bottom', end: 'bottom top', scrub: true } });
      var ws = $$('.qw', q);
      if (ws.length) gsap.to(ws, { opacity: 1, stagger: .1, ease: 'none', scrollTrigger: { trigger: $('blockquote', q), start: 'top 82%', end: 'bottom 45%', scrub: true } });
    });

    /* Portrait et bloc noir décalés */
    $$('.duo-media').forEach(function (d) {
      gsap.fromTo($('.duo-block', d), { yPercent: 8 }, { yPercent: -8, ease: 'none', scrollTrigger: { trigger: d, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* Séquence épinglée (bureau) */
    ScrollTrigger.matchMedia({ '(min-width: 961px)': function () {
      $$('.sequence').forEach(function (sq) {
        var figs = $$('.seq-media figure', sq), steps = $$('.seq-steps li', sq), fig = $('.seq-fig', sq);
        var cnt = $('.seq-count b', sq), prog = $('.seq-prog i', sq), n = figs.length, cur = 0;
        var tl = gsap.timeline({ scrollTrigger: { trigger: sq, start: 'top top', end: '+=' + (n * 90) + '%', pin: $('.seq-stage', sq), scrub: .7,
          onUpdate: function (st) {
            var k = Math.min(n - 1, Math.floor(st.progress * n * 0.999));
            if (prog) prog.style.transform = 'scaleX(' + st.progress + ')';
            if (k !== cur) { steps.forEach(function (s, j) { s.classList.toggle('is-on', j === k); }); cur = k; if (cnt) cnt.textContent = ('0' + (k + 1)).slice(-2); }
            if (fig) fig.classList.toggle('is-on', st.progress > .78);
          } } });
        figs.forEach(function (f, i) {
          var im = $('img', f);
          if (i > 0) tl.fromTo(f, { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'power2.inOut', duration: .55 }, i - .35);
          tl.fromTo(im, { scale: 1.16 }, { scale: 1, ease: 'none', duration: 1.2 }, i === 0 ? 0 : i - .35);
        });
        tl.to({}, { duration: .3 });
      });
    } });

    /* Frise qui se dessine */
    $$('.timeline').forEach(function (t) {
      var bar = $('.tl-bar i', t);
      gsap.fromTo(bar, { height: '0%' }, { height: '100%', ease: 'none', scrollTrigger: { trigger: t, start: 'top 70%', end: 'bottom 65%', scrub: true } });
    });

    /* Photos des rangées : léger décalage au défilement */
    $$('.row-media img').forEach(function (im) {
      gsap.fromTo(im.parentElement, { y: 40 }, { y: -40, ease: 'none', scrollTrigger: { trigger: im.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
  } else {
    $$('.quote .qw').forEach(function (w) { w.style.opacity = 1; });
    $$('.tl-bar i').forEach(function (b) { b.style.height = '100%'; });
    $$('.seq-steps li').forEach(function (s, j) { s.classList.toggle('is-on', j === 0); });
  }

  /* ---------- Filtres des réalisations ---------- */
  var filters = $('.filters');
  if (filters) {
    var grid = $('.mosaic'), tiles = $$('.mosaic .tile');
    var apply = function (f, push) {
      $$('button', filters).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-filter') === f ? 'true' : 'false'); });
      grid.classList.toggle('filtered', f !== 'tout');
      tiles.forEach(function (t) {
        var show = f === 'tout' || t.getAttribute('data-cat') === f;
        t.classList.toggle('is-hidden', !show);
        if (show) { t.classList.remove('in'); void t.offsetWidth; requestAnimationFrame(function () { t.classList.add('in'); }); }
      });
      var live = $('.filter-live'); if (live) live.textContent = tiles.filter(function (t) { return !t.classList.contains('is-hidden'); }).length + ' projet(s) affiché(s)';
      if (push) history.replaceState(null, '', f === 'tout' ? location.pathname : '#' + encodeURIComponent(f));
      if (hasGsap) ScrollTrigger.refresh();
    };
    filters.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) apply(b.getAttribute('data-filter'), true); });
    var h = decodeURIComponent(location.hash.slice(1));
    if (h && $('[data-filter="' + h + '"]', filters)) apply(h, false);
  }

  /* ---------- Visionneuse ---------- */
  var shots = $$('button.shot');
  if (shots.length) {
    var lb = doc.createElement('div');
    lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo agrandie');
    lb.innerHTML = '<img alt=""><button class="lb-close" type="button">Fermer ✕</button><button class="lb-prev" type="button">← Préc.</button><button class="lb-next" type="button">Suiv. →</button><span class="lb-count"></span>';
    body.appendChild(lb);
    var lim = $('img', lb), cnt = $('.lb-count', lb), cur = 0, last = null;
    var show = function (i) {
      cur = (i + shots.length) % shots.length;
      lim.classList.add('is-swapping');
      var nimg = new Image();
      nimg.onload = function () { lim.src = nimg.src; lim.alt = $('img', shots[cur]).alt; lim.classList.remove('is-swapping'); };
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

  /* ---------- Heure de Vienne ---------- */
  var clock = $('[data-clock]');
  if (clock) {
    var tick = function () { try { clock.textContent = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris' }).format(new Date()); } catch (e) {} };
    tick(); setInterval(tick, 30000);
  }

  /* ---------- Souris : curseur, photo des principes, ouverture qui suit ---------- */
  if (fine && !reduce) {
    var cu = $('.cursor'), cl = cu && $('span', cu), cx = innerWidth / 2, cy = innerHeight / 2, tx = cx, ty = cy;
    var pf = null, pfx = 0, pfy = 0;
    if ($('.pr[data-img]')) {
      pf = doc.createElement('div'); pf.className = 'pr-float'; pf.setAttribute('aria-hidden', 'true'); pf.innerHTML = '<img alt="">';
      body.appendChild(pf);
      $$('.pr[data-img]').forEach(function (p) {
        p.addEventListener('mouseenter', function () { $('img', pf).src = p.getAttribute('data-img'); pf.classList.add('on'); });
        p.addEventListener('mouseleave', function () { pf.classList.remove('on'); });
      });
    }
    window.addEventListener('mousemove', function (e) { tx = e.clientX; ty = e.clientY; if (cu) cu.classList.add('on'); }, { passive: true });
    doc.addEventListener('mouseleave', function () { if (cu) cu.classList.remove('on'); });
    (function loop() {
      cx += (tx - cx) * .2; cy += (ty - cy) * .2;
      if (cu) cu.style.transform = 'translate(' + cx + 'px,' + cy + 'px)';
      if (pf) { pfx += (tx + 170 - pfx) * .1; pfy += (ty - pfy) * .1; pf.style.left = pfx + 'px'; pf.style.top = pfy + 'px'; }
      requestAnimationFrame(loop);
    })();
    if (cu) doc.addEventListener('mouseover', function (e) {
      var lab = e.target.closest('[data-cursor], .tile, button.shot, .pn-a');
      var hov = e.target.closest('a, button, input, textarea, select, .pr');
      cu.classList.toggle('label', !!lab);
      cu.classList.toggle('hover', !lab && !!hov);
      cu.classList.toggle('light', !!e.target.closest('.hero, .quote, .pn-a, .lightbox'));
      if (lab) cl.textContent = lab.getAttribute('data-cursor') || (lab.tagName === 'BUTTON' ? 'Agrandir' : 'Voir');
    });
    $$('.hero').forEach(function (sec) {
      var bg = $('.slides', sec);
      sec.addEventListener('mousemove', function (e) {
        var r = sec.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        bg.style.translate = (-x * 18).toFixed(1) + 'px ' + (-y * 12).toFixed(1) + 'px';
      });
      sec.addEventListener('mouseleave', function () { bg.style.translate = '0 0'; });
    });
  }

  /* ---------- Haut de page ---------- */
  var tt = $('.to-top');
  if (tt) tt.addEventListener('click', function () { if (lenis) lenis.scrollTo(0, { duration: 1.6 }); else window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
  $$('.hero-down').forEach(function (a) {
    a.addEventListener('click', function (e) { var t = $('#suite'); if (lenis && t) { e.preventDefault(); lenis.scrollTo(t, { duration: 1.4, offset: -40 }); } });
  });

  window.addEventListener('load', function () { if (hasGsap) ScrollTrigger.refresh(); });
})();
