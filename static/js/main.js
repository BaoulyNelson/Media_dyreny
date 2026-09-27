/* =========================================
   LE MÉDIA — JavaScript Principal
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Bouton retour en haut ─────────────────────────────── */
  const btn = document.getElementById('backToTop');
  if (btn) {
    window.addEventListener('scroll', () => {
      btn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  /* ── Auto-fermeture des messages flash (5 s) ───────────── */
  setTimeout(() => {
    document.querySelectorAll('.alert.fade.show').forEach(el => {
      bootstrap.Alert.getOrCreateInstance(el)?.close();
    });
  }, 5000);

  /* ── Compteur de caractères (commentaires) ─────────────── */
  const textarea = document.querySelector('textarea[name="contenu"]');
  if (textarea) {
    const max = parseInt(textarea.getAttribute('maxlength')) || 1000;
    const counter = document.createElement('small');
    counter.className = 'text-muted d-block text-end mt-1';
    counter.textContent = `0 / ${max} caractères`;
    textarea.parentNode.insertBefore(counter, textarea.nextSibling);
    textarea.addEventListener('input', () => {
      const len = textarea.value.length;
      counter.textContent = `${len} / ${max} caractères`;
      counter.className = len > max * 0.9
        ? 'text-warning d-block text-end mt-1'
        : 'text-muted d-block text-end mt-1';
    });
  }



  /* ── Lazy loading images ───────────────────────────────── */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.src = e.target.dataset.src; io.unobserve(e.target); }
      });
    });
    document.querySelectorAll('img[data-src]').forEach(img => io.observe(img));
  }

  /* ══════════════════════════════════════════════════════════
     MOBILE — Recherche dépliable
     ══════════════════════════════════════════════════════ */
  const searchToggle = document.getElementById('mobileSearchToggle');
  const searchBar    = document.getElementById('mobileSearchBar');
  const searchIcon   = document.getElementById('searchIcon');

  if (searchToggle && searchBar) {
    searchToggle.addEventListener('click', () => {
      const open = searchBar.classList.toggle('open');
      searchIcon.className = open ? 'bi bi-x-lg' : 'bi bi-search';
      if (open) searchBar.querySelector('input')?.focus();
    });
  }

  /* ══════════════════════════════════════════════════════════
     MOBILE — Panel catégories (bottom sheet)
     ══════════════════════════════════════════════════════ */
  const btnCat  = document.getElementById('btnCategoriesMobile');
  const panel   = document.getElementById('catPanel');
  const overlay = document.getElementById('catPanelOverlay');
  const closeBtn = document.getElementById('closeCatPanel');

  function openPanel() {
    panel?.classList.add('open');
    overlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closePanel() {
    panel?.classList.remove('open');
    overlay?.classList.remove('show');
    document.body.style.overflow = '';
  }

  btnCat?.addEventListener('click', openPanel);
  closeBtn?.addEventListener('click', closePanel);
  overlay?.addEventListener('click', closePanel);

  /* Fermer en swipant vers le bas */
  if (panel) {
    let startY = 0;
    panel.addEventListener('touchstart', e => { startY = e.touches[0].clientY; }, { passive: true });
    panel.addEventListener('touchend',   e => {
      if (e.changedTouches[0].clientY - startY > 60) closePanel();
    }, { passive: true });
    /* Fermer quand on clique un lien dans le panel */
    panel.querySelectorAll('a').forEach(a => a.addEventListener('click', closePanel));
  }

  /* ══════════════════════════════════════════════════════════
     Highlighting actif de la bottom nav (complément Django)
     ══════════════════════════════════════════════════════ */
  const path = window.location.pathname;
  document.querySelectorAll('.mobile-nav-item[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href || href === '#') return;
    if ((href === '/' && path === '/') || (href !== '/' && path.startsWith(href))) {
      link.classList.add('active');
    }
  });

});
