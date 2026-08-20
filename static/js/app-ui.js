(function () {
  'use strict';

  // ================================================
  // Kobaia QR — Orden del catálogo (app-ui.js)
  // Complemento independiente que añade ordenación al
  // catálogo. Solo reordena los .card-item ya renderizados
  // por app.js y NO altera su lógica funcional (la búsqueda
  // sigue siendo gestionada por app.js en cardsSearchInput).
  // ================================================

  var sortSelect = document.getElementById('catalogSortSelect');
  var catalogGrid = document.getElementById('cardsCatalogGrid');

  function cards() {
    return catalogGrid ? Array.prototype.slice.call(catalogGrid.querySelectorAll('.card-item')) : [];
  }

  function scanCountOf(el) {
    var badge = el.querySelector('.scan-badge');
    if (!badge) return 0;
    var m = (badge.textContent || '').match(/(\d+)/);
    return m ? parseInt(m[1], 10) : 0;
  }

  function describe(el) {
    var typeBadge = el.querySelector('.card-item-meta .badge');
    var isDynamic = typeBadge ? /dinámic/i.test(typeBadge.textContent) : true;
    return {
      el: el,
      title: (el.querySelector('.card-item-title') || {}).textContent || '',
      scans: scanCountOf(el),
      dynamic: isDynamic
    };
  }

  function applySort(mode) {
    if (!catalogGrid) return;
    var list = cards().map(describe);

    switch (mode) {
      case 'title':
        list.sort(function (a, b) { return a.title.localeCompare(b.title, 'es'); });
        break;
      case 'scans':
        list.sort(function (a, b) { return b.scans - a.scans; });
        break;
      case 'static':
        list.sort(function (a, b) { return (a.dynamic === b.dynamic) ? 0 : (a.dynamic ? 1 : -1); });
        break;
      case 'dynamic':
        list.sort(function (a, b) { return (a.dynamic === b.dynamic) ? 0 : (a.dynamic ? -1 : 1); });
        break;
      case 'recent':
      default:
        return; // mantiene el orden natural del objeto
    }

    list.forEach(function (item) { catalogGrid.appendChild(item.el); });
  }

  function init() {
    if (sortSelect) {
      sortSelect.addEventListener('change', function () { applySort(sortSelect.value); });
      sortSelect.addEventListener('click', function () { applySort(sortSelect.value); });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
