document.addEventListener('DOMContentLoaded', () => {
  if (window.__researchIndexFiltersInitialized) return;
  const shell = document.querySelector('.site-shell[data-page="research"]');
  const listingContainer = document.querySelector('#listing-research-index');
  const listing = listingContainer?.querySelector('.research-listing');
  const empty = document.querySelector('.research-filter-empty');
  if (!shell || !listing || !empty) return;

  window.__researchIndexFiltersInitialized = true;

  shell.querySelector('.research-category-nav')?.remove();

  const entries = Array.from(listing.querySelectorAll('.research-entry'));
  const lineButtons = Array.from(shell.querySelectorAll('[data-research-line-filter]'));
  lineButtons.forEach((button) => {
    button.setAttribute('aria-controls', listingContainer.id);
  });
  const spanish = document.documentElement.lang === 'es';
  let selectedLine = 'all';

  const update = () => {
    let visible = 0;
    entries.forEach((entry) => {
      const show = selectedLine === 'all' || entry.dataset.researchLine === selectedLine;
      entry.hidden = !show;
      if (show) visible += 1;
    });
    lineButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.researchLineFilter === selectedLine));
    });
    empty.hidden = visible !== 0;
    if (visible === 0) {
      empty.innerHTML = spanish
        ? 'No hay publicaciones para esta combinación. <button type="button" class="research-filter-reset">Restablecer filtros</button>'
        : 'No publications match this combination. <button type="button" class="research-filter-reset">Reset filters</button>';
    }
  };

  lineButtons.forEach((button) => button.addEventListener('click', () => {
    selectedLine = button.dataset.researchLineFilter || 'all';
    update();
  }));
  empty.addEventListener('click', (event) => {
    if (!event.target.closest('.research-filter-reset')) return;
    selectedLine = 'all';
    update();
  });
  update();
});
