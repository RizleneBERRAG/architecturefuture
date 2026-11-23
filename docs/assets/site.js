(function () {
  'use strict';
  var doc = document, html = doc.documentElement, body = doc.body;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var hasGsap = !!(window.gsap && window.ScrollTrigger) && !reduce;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var lenis = null;

  /* ---------- Défilement doux ---------- */
  if (hasGsap) {
    gsap.registerPlugin(ScrollTrigger);
    if (window.Lenis) {
      lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 1 });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }
  }

  /* ---------- En-tête : plein après le héros, masqué en descendant ---------- */
  var header = $('.site-header');
  var hero = $('.hero-imm, .page-hero');
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    var limit = hero ? Math.max(hero.offsetHeight - 90, 40) : 30;
    header.classList.toggle('is-solid', body.classList.contains('head-solid') || y > limit);
    if (!body.classList.contains('menu-open')) header.classList.toggle('is-hidden', y > 400 && y > lastY + 2);
    if (y < lastY - 2) header.classList.remove('is-hidden');
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Menu plein écran ---------- */
  var mbtn = $('.menu-btn');
  if (mbtn) {
    mbtn.addEventListener('click', function () {
      var open = body.classList.toggle('menu-open');
      mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      $('.lbl', mbtn).textContent = open ? 'Fermer' : 'Menu';
      if (lenis) open ? lenis.stop() : lenis.start();
    });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && body.classList.contains('menu-open')) mbtn.click(); });
  }

  /* ---------- Rideau entre les pages ---------- */
  if (!reduce) {
    doc.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      var href = a.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto|tel|https?):/.test(href)) return;
      e.preventDefault();
      body.classList.add('leaving');
      setTimeout(function () { window.location.href = href; }, 520);
    });
    window.addEventListener('pageshow', function (e) { if (e.persisted) body.classList.remove('leaving'); });
  }

  /* ---------- Curseur ---------- */
  var cursor = $('.cursor');
  if (cursor && fine && !reduce) {
    var cx = innerWidth / 2, cy = innerHeight / 2, tx = cx, ty = cy;
    window.addEventListener('mousemove', function (e) { tx = e.clientX; ty = e.clientY; cursor.classList.add('is-on'); }, { passive: true });
    doc.addEventListener('mouseleave', function () { cursor.classList.remove('is-on'); });
    (function loop() { cx += (tx - cx) * 0.2; cy += (ty - cy) * 0.2; cursor.style.transform = 'translate(' + cx + 'px,' + cy + 'px)'; requestAnimationFrame(loop); })();
    doc.addEventListener('mouseover', function (e) {
      var t = e.target.closest('[data-cursor]');
      cursor.classList.toggle('is-big', !!t);
      if (t) $('.lbl', cursor).textContent = t.getAttribute('data-cursor');
    });
  }

  /* ---------- Diaporama du héros ---------- */
  var slides = $$('.hero-imm .slide');
  if (slides.length > 1) {
    var bars = $$('.hero-imm .progress i'), cap = $('.hero-foot [data-caption]'), cnt = $('.hero-imm [data-count]'), cur = 0;
    function go(i) {
      slides[cur].classList.remove('is-active');
      cur = i % slides.length;
      slides[cur].classList.add('is-active');
      bars.forEach(function (b, k) { b.classList.toggle('is-done', k < cur); b.classList.remove('is-active'); });
      if (bars[cur]) { void bars[cur].offsetWidth; bars[cur].classList.add('is-active'); }
      if (cap) cap.textContent = slides[cur].getAttribute('data-caption');
      if (cnt) cnt.textContent = ('0' + (cur + 1)).slice(-2) + ' / ' + ('0' + slides.length).slice(-2);
    }
    go(0);
    if (!reduce) setInterval(function () { go(cur + 1); }, 6000);
  }

  /* ---------- Apparitions ---------- */
  var watched = $$('.reveal, .img-reveal, .split');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); } });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.01 });
    watched.forEach(function (el) { io.observe(el); });
  } else watched.forEach(function (el) { el.classList.add('is-in'); });

  /* ---------- Manifeste qui s’allume mot à mot ---------- */
  $$('[data-words]').forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map(function (w) { return '<span class="w">' + w + '</span>'; }).join(' ');
    var ws = $$('.w', el);
    if (hasGsap) {
      gsap.to(ws, { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: el, start: 'top 80%', end: 'bottom 45%', scrub: true } });
    } else ws.forEach(function (w) { w.style.opacity = 1; });
  });

  if (hasGsap) {
    /* ---------- Principes : séquence épinglée ---------- */
    $$('.pin-seq').forEach(function (seq) {
      var steps = $$('.pin-step', seq), imgs = $$('.pin-img', seq), pbars = $$('.pin-bar i', seq), lab = $('.pin-label', seq);
      var n = steps.length;
      var tl = gsap.timeline({
        scrollTrigger: {
          trigger: seq, start: 'top top', end: '+=' + (n * 90) + '%', pin: $('.pin-stage', seq), scrub: 0.6,
          onUpdate: function (st) {
            var p = st.progress * n;
            pbars.forEach(function (b, k) { b.style.setProperty('--p', Math.max(0, Math.min(1, p - k))); });
            if (lab) lab.textContent = ('0' + Math.min(n, Math.floor(p) + 1)).slice(-2) + ' / ' + ('0' + n).slice(-2);
          }
        }
      });
      for (var i = 1; i < n; i++) {
        tl.to(steps[i - 1], { opacity: 0, y: -40, duration: 0.4 }, i)
          .fromTo(imgs[i], { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1, ease: 'power2.inOut' }, i - 0.3)
          .fromTo($('img', imgs[i]), { scale: 1.25 }, { scale: 1, duration: 1.2, ease: 'power2.out' }, i - 0.3)
          .fromTo(steps[i], { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5 }, i + 0.2);
      }
      tl.to({}, { duration: 0.6 });
    });

    /* ---------- Réalisations en défilement horizontal (bureau) ---------- */
    ScrollTrigger.matchMedia({
      '(min-width: 761px)': function () {
        $$('.hscroll').forEach(function (sec) {
          var track = $('.hs-track', sec);
          var dist = function () { return Math.max(0, track.scrollWidth - innerWidth); };
          gsap.to(track, {
            x: function () { return -dist(); }, ease: 'none',
            scrollTrigger: { trigger: $('.hs-viewport', sec), start: 'top top', end: function () { return '+=' + dist(); }, pin: true, scrub: 0.8, invalidateOnRefresh: true }
          });
        });
      }
    });

    /* ---------- Parallaxe ---------- */
    $$('[data-speed]').forEach(function (el) {
      var s = parseFloat(el.getAttribute('data-speed')) || 10;
      gsap.fromTo(el, { yPercent: -s }, { yPercent: s, ease: 'none', scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* ---------- Frise chronologique ---------- */
    $$('.timeline').forEach(function (t) {
      var bar = $('.tl-progress', t);
      ScrollTrigger.create({ trigger: t, start: 'top 70%', end: 'bottom 60%', scrub: true, onUpdate: function (st) { bar.style.setProperty('--p', st.progress); } });
    });
  } else {
    $$('.timeline .tl-progress').forEach(function (b) { b.style.setProperty('--p', 1); });
    $$('.pin-bar i').forEach(function (b) { b.style.setProperty('--p', 1); });
  }

  /* ---------- Chiffres qui défilent ---------- */
  $$('[data-to]').forEach(function (el) {
    var to = parseFloat(el.getAttribute('data-to')), dec = parseInt(el.getAttribute('data-dec') || '0', 10), pre = el.getAttribute('data-pre') || '';
    var fmt = function (v) { return pre + v.toFixed(dec).replace('.', ','); };
    if (reduce || !('IntersectionObserver' in window)) { el.textContent = fmt(to); return; }
    el.textContent = fmt(0);
    var o = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return; o.disconnect();
      var t0 = performance.now();
      (function step(t) { var k = Math.min(1, (t - t0) / 1800); var e = 1 - Math.pow(1 - k, 4); el.textContent = fmt(to * e); if (k < 1) requestAnimationFrame(step); })(t0);
    }, { threshold: 0.6 });
    o.observe(el);
  });

  /* ---------- Image qui suit la souris (index, compétences) ---------- */
  var hov = $('.hover-img');
  if (hov && fine) {
    var hx = 0, hy = 0, mx = 0, my = 0, himg = $('img', hov);
    window.addEventListener('mousemove', function (e) { mx = e.clientX; my = e.clientY; }, { passive: true });
    (function loop() { hx += (mx - hx) * 0.14; hy += (my - hy) * 0.14; hov.style.left = hx + 'px'; hov.style.top = hy + 'px'; requestAnimationFrame(loop); })();
    $$('[data-img]').forEach(function (r) {
      r.addEventListener('mouseenter', function () { himg.src = r.getAttribute('data-img'); hov.classList.add('is-on'); });
      r.addEventListener('mouseleave', function () { hov.classList.remove('is-on'); });
    });
  }

  /* ---------- Filtres et vue des réalisations ---------- */
  var filters = $('.filters');
  if (filters) {
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      $$('button', filters).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      var f = b.getAttribute('data-filter');
      $$('[data-cat]').forEach(function (c) { c.hidden = !(f === 'tout' || c.getAttribute('data-cat') === f); });
      if (hasGsap) ScrollTrigger.refresh();
    });
  }
  var vt = $('.view-toggle');
  if (vt) {
    vt.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      $$('button', vt).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $('.p-wrap').classList.toggle('view-grid', b.getAttribute('data-view') === 'grid');
      $$('.g-card').forEach(function (c) { c.classList.add('is-in'); });
      if (hasGsap) ScrollTrigger.refresh();
    });
  }

  /* ---------- Bande photo d’un projet : glisser + visionneuse ---------- */
  var strip = $('.strip');
  if (strip) {
    var down = false, sx = 0, sl = 0, moved = false;
    strip.addEventListener('mousedown', function (e) { down = true; moved = false; sx = e.pageX; sl = strip.scrollLeft; strip.classList.add('is-drag'); });
    window.addEventListener('mouseup', function () { down = false; strip.classList.remove('is-drag'); });
    strip.addEventListener('mousemove', function (e) { if (!down) return; var dx = e.pageX - sx; if (Math.abs(dx) > 4) moved = true; strip.scrollLeft = sl - dx; });
    strip.addEventListener('wheel', function (e) { if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && strip.scrollWidth > strip.clientWidth) { var before = strip.scrollLeft; strip.scrollLeft += e.deltaY; if (strip.scrollLeft !== before) e.preventDefault(); } }, { passive: false });
    strip.setAttribute('data-lenis-prevent-wheel', '');

    var shots = $$('button', strip);
    var lb = doc.createElement('div');
    lb.className = 'lightbox'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Photo agrandie');
    lb.innerHTML = '<img alt=""><button class="lb-close" type="button">Fermer ✕</button><button class="lb-prev" type="button">← Préc.</button><button class="lb-next" type="button">Suiv. →</button><span class="lb-count"></span>';
    body.appendChild(lb);
    var lbi = $('img', lb), lbc = $('.lb-count', lb), at = 0, last = null;
    var show = function (i) { at = (i + shots.length) % shots.length; lbi.src = shots[at].getAttribute('data-full'); lbi.alt = $('img', shots[at]).alt; lbc.textContent = (at + 1) + ' / ' + shots.length; };
    var close = function () { lb.classList.remove('is-open'); if (lenis) lenis.start(); if (last) last.focus(); };
    shots.forEach(function (s, i) {
      s.addEventListener('click', function (e) { if (moved) { e.preventDefault(); return; } last = s; show(i); lb.classList.add('is-open'); if (lenis) lenis.stop(); $('.lb-close', lb).focus(); });
    });
    $('.lb-close', lb).addEventListener('click', close);
    $('.lb-prev', lb).addEventListener('click', function () { show(at - 1); });
    $('.lb-next', lb).addEventListener('click', function () { show(at + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    doc.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(at - 1); if (e.key === 'ArrowRight') show(at + 1);
    });
  }

  /* ---------- Formulaire : ouvre la messagerie ---------- */
  var form = $('#contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = function (n) { return ((form.elements[n] && form.elements[n].value) || '').trim(); };
      var subject = 'Demande de contact' + (v('projet') ? ' — ' + v('projet') : '');
      var text = v('message') + '\n\n' + v('nom') + (v('tel') ? '\n' + v('tel') : '') + (v('email') ? '\n' + v('email') : '') + (v('lieu') ? '\nLieu du projet : ' + v('lieu') : '');
      window.location.href = 'mailto:' + form.getAttribute('data-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
    });
  }

  window.addEventListener('load', function () { if (hasGsap) ScrollTrigger.refresh(); });
})();
