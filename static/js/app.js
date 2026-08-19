/**
 * QR Digital Studio - Frontend Application Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  // Estado global de la aplicación
  const state = {
    contentType: 'url',
    cardId: 'macrojaguar',
    cardTitle: 'Macro Jaguar QR',
    logoPath: 'img/MacroJG.png',
    fillColor: '#000000',
    backColor: '#FFFFFF',
    logoSizeRatio: 0.22,
    border: 4,
    errorCorrection: 'H',
    cachedTarjetas: {},
    availableLogos: []
  };

  // Referencias a elementos del DOM
  const dom = {
    themeToggleBtn: document.getElementById('themeToggleBtn'),
    tabDesignerBtn: document.getElementById('tabDesignerBtn'),
    tabCatalogBtn: document.getElementById('tabCatalogBtn'),
    designerSection: document.getElementById('designerSection'),
    catalogSection: document.getElementById('catalogSection'),
    cardsCountBadge: document.getElementById('cardsCountBadge'),
    
    // Selectores de tipo
    typeBtns: document.querySelectorAll('.type-btn'),
    typeForms: document.querySelectorAll('.type-form'),

    // Inputs generales
    cardIdInput: document.getElementById('cardIdInput'),
    cardTitleInput: document.getElementById('cardTitleInput'),
    urlInput: document.getElementById('urlInput'),
    
    // vCard inputs
    vcardName: document.getElementById('vcardName'),
    vcardOrg: document.getElementById('vcardOrg'),
    vcardTitle: document.getElementById('vcardTitle'),
    vcardPhone: document.getElementById('vcardPhone'),
    vcardEmail: document.getElementById('vcardEmail'),
    vcardUrl: document.getElementById('vcardUrl'),

    // WhatsApp & WiFi & Text
    waPhone: document.getElementById('waPhone'),
    waMessage: document.getElementById('waMessage'),
    wifiSsid: document.getElementById('wifiSsid'),
    wifiAuth: document.getElementById('wifiAuth'),
    wifiPassword: document.getElementById('wifiPassword'),
    textInput: document.getElementById('textInput'),

    // Logotipo
    logoDropZone: document.getElementById('logoDropZone'),
    logoFileInput: document.getElementById('logoFileInput'),
    logoPreviewBar: document.getElementById('logoPreviewBar'),
    logoThumbImg: document.getElementById('logoThumbImg'),
    logoNameLabel: document.getElementById('logoNameLabel'),
    removeLogoBtn: document.getElementById('removeLogoBtn'),
    logoStatusBadge: document.getElementById('logoStatusBadge'),
    availableLogosGrid: document.getElementById('availableLogosGrid'),

    // Estilos y colores
    fillColorPicker: document.getElementById('fillColorPicker'),
    fillColorHex: document.getElementById('fillColorHex'),
    backColorPicker: document.getElementById('backColorPicker'),
    backColorHex: document.getElementById('backColorHex'),
    presetPills: document.querySelectorAll('.preset-pill'),
    logoSizeSlider: document.getElementById('logoSizeSlider'),
    logoSizeVal: document.getElementById('logoSizeVal'),
    borderSlider: document.getElementById('borderSlider'),
    borderVal: document.getElementById('borderVal'),

    // Previsualizador
    qrPreviewImg: document.getElementById('qrPreviewImg'),
    qrLoadingOverlay: document.getElementById('qrLoadingOverlay'),
    previewStatusText: document.getElementById('previewStatusText'),
    previewTargetUrl: document.getElementById('previewTargetUrl'),

    // Acciones
    downloadPngBtn: document.getElementById('downloadPngBtn'),
    downloadSvgBtn: document.getElementById('downloadSvgBtn'),
    saveToCatalogBtn: document.getElementById('saveToCatalogBtn'),
    copyImageBtn: document.getElementById('copyImageBtn'),
    exportZipTopBtn: document.getElementById('exportZipTopBtn'),
    exportAllZipBtn: document.getElementById('exportAllZipBtn'),
    newCardBtn: document.getElementById('newCardBtn'),

    // Catálogo
    cardsCatalogGrid: document.getElementById('cardsCatalogGrid'),
    cardsSearchInput: document.getElementById('cardsSearchInput'),
    toastContainer: document.getElementById('toastContainer')
  };

  let debounceTimer = null;

  // ==========================================
  // INICIALIZACIÓN
  // ==========================================
  function init() {
    initTheme();
    setupEventListeners();
    loadAvailableLogos();
    loadCatalog();
    triggerLivePreview();
  }

  // ==========================================
  // TEMA OSCURO / CLARO
  // ==========================================
  function initTheme() {
    const savedTheme = localStorage.getItem('qr_studio_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('qr_studio_theme', newTheme);
    showToast(`Modo ${newTheme === 'dark' ? 'oscuro' : 'claro'} activado`, 'info');
  }

  // ==========================================
  // NAVEGACIÓN POR PESTAÑAS
  // ==========================================
  function switchTab(tabId) {
    if (tabId === 'designerSection') {
      dom.tabDesignerBtn.classList.add('active');
      dom.tabCatalogBtn.classList.remove('active');
      dom.designerSection.classList.add('active');
      dom.catalogSection.classList.remove('active');
    } else {
      dom.tabCatalogBtn.classList.add('active');
      dom.tabDesignerBtn.classList.remove('active');
      dom.catalogSection.classList.add('active');
      dom.designerSection.classList.remove('active');
      loadCatalog();
    }
  }

  // ==========================================
  // CONFIGURACIÓN DE EVENTOS
  // ==========================================
  function setupEventListeners() {
    // Theme toggle
    dom.themeToggleBtn.addEventListener('click', toggleTheme);

    // Navegación
    dom.tabDesignerBtn.addEventListener('click', () => switchTab('designerSection'));
    dom.tabCatalogBtn.addEventListener('click', () => switchTab('catalogSection'));
    dom.newCardBtn?.addEventListener('click', () => {
      resetToDefaultCard();
      switchTab('designerSection');
    });

    // Content Type Selector
    dom.typeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        dom.typeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.contentType = btn.dataset.type;

        dom.typeForms.forEach(f => f.classList.remove('active'));
        const targetForm = document.getElementById(`formType${capitalize(state.contentType)}`);
        if (targetForm) targetForm.classList.add('active');

        triggerLivePreview();
      });
    });

    // Inputs reactivos para previsualización instantánea
    const reactiveInputs = [
      dom.cardIdInput, dom.cardTitleInput, dom.urlInput,
      dom.vcardName, dom.vcardOrg, dom.vcardTitle, dom.vcardPhone, dom.vcardEmail, dom.vcardUrl,
      dom.waPhone, dom.waMessage, dom.wifiSsid, dom.wifiAuth, dom.wifiPassword, dom.textInput
    ];

    reactiveInputs.forEach(input => {
      if (input) {
        input.addEventListener('input', () => {
          if (input === dom.cardIdInput) state.cardId = input.value;
          if (input === dom.cardTitleInput) state.cardTitle = input.value;
          triggerLivePreview();
        });
      }
    });

    // Sincronización de Color Fill
    dom.fillColorPicker.addEventListener('input', (e) => {
      dom.fillColorHex.value = e.target.value;
      state.fillColor = e.target.value;
      triggerLivePreview();
    });
    dom.fillColorHex.addEventListener('input', (e) => {
      if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
        dom.fillColorPicker.value = e.target.value;
        state.fillColor = e.target.value;
        triggerLivePreview();
      }
    });

    // Sincronización de Color Back
    dom.backColorPicker.addEventListener('input', (e) => {
      dom.backColorHex.value = e.target.value;
      state.backColor = e.target.value;
      triggerLivePreview();
    });
    dom.backColorHex.addEventListener('input', (e) => {
      if (/^#[0-9A-F]{6}$/i.test(e.target.value)) {
        dom.backColorPicker.value = e.target.value;
        state.backColor = e.target.value;
        triggerLivePreview();
      }
    });

    // Color Presets
    dom.presetPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const fill = pill.dataset.fill;
        const back = pill.dataset.back;
        dom.fillColorPicker.value = fill;
        dom.fillColorHex.value = fill;
        dom.backColorPicker.value = back;
        dom.backColorHex.value = back;
        state.fillColor = fill;
        state.backColor = back;
        triggerLivePreview();
      });
    });

    // Sliders
    dom.logoSizeSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      dom.logoSizeVal.textContent = `${val}%`;
      state.logoSizeRatio = val / 100;
      triggerLivePreview();
    });

    dom.borderSlider.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      dom.borderVal.textContent = `${val} bloques`;
      state.border = val;
      triggerLivePreview();
    });

    // Drag & Drop / Selección de Logo
    dom.logoDropZone.addEventListener('click', () => dom.logoFileInput.click());
    dom.logoFileInput.addEventListener('change', handleLogoFileSelect);

    ['dragenter', 'dragover'].forEach(eventName => {
      dom.logoDropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dom.logoDropZone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dom.logoDropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dom.logoDropZone.classList.remove('dragover');
      });
    });

    dom.logoDropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        uploadLogoFile(files[0]);
      }
    });

    dom.removeLogoBtn.addEventListener('click', () => {
      state.logoPath = null;
      updateLogoUI(null);
      triggerLivePreview();
      showToast('Logotipo removido del QR', 'info');
    });

    // Botones de Descarga
    dom.downloadPngBtn.addEventListener('click', () => downloadFile('png'));
    dom.downloadSvgBtn.addEventListener('click', () => downloadFile('svg'));
    dom.exportZipTopBtn.addEventListener('click', downloadAllZip);
    dom.exportAllZipBtn.addEventListener('click', downloadAllZip);

    // Guardar en Catálogo
    dom.saveToCatalogBtn.addEventListener('click', saveCurrentCardToCatalog);

    // Copiar Imagen al portapapeles
    dom.copyImageBtn.addEventListener('click', copyQrImageToClipboard);

    // Buscador en Catálogo
    dom.cardsSearchInput?.addEventListener('input', filterCatalogCards);
  }

  // ==========================================
  // CONSTRUCCIÓN DEL PAYLOAD PARA LA API
  // ==========================================
  function buildPayload(format = 'png') {
    const cardId = dom.cardIdInput.value.trim() || 'tarjeta_qr';
    const payload = {
      content_type: state.contentType,
      fill_color: state.fillColor,
      back_color: state.backColor,
      logo_path: state.logoPath || null,
      logo_size_ratio: state.logoSizeRatio,
      border: state.border,
      error_correction: state.errorCorrection,
      format: format,
      filename: cardId
    };

    if (state.contentType === 'url') {
      payload.data = dom.urlInput.value.trim() || 'https://example.com';
    } else if (state.contentType === 'vcard') {
      payload.vcard = {
        name: dom.vcardName.value.trim(),
        org: dom.vcardOrg.value.trim(),
        title: dom.vcardTitle.value.trim(),
        phone: dom.vcardPhone.value.trim(),
        email: dom.vcardEmail.value.trim(),
        url: dom.vcardUrl.value.trim()
      };
    } else if (state.contentType === 'whatsapp') {
      payload.whatsapp = {
        phone: dom.waPhone.value.trim(),
        message: dom.waMessage.value.trim()
      };
    } else if (state.contentType === 'wifi') {
      payload.wifi = {
        ssid: dom.wifiSsid.value.trim(),
        password: dom.wifiPassword.value.trim(),
        auth_type: dom.wifiAuth.value,
        hidden: false
      };
    } else {
      payload.data = dom.textInput.value.trim();
    }

    return payload;
  }

  // ==========================================
  // PREVISUALIZACIÓN EN TIEMPO REAL (DEBOUNCED)
  // ==========================================
  function triggerLivePreview() {
    clearTimeout(debounceTimer);
    dom.qrLoadingOverlay.classList.add('active');

    debounceTimer = setTimeout(async () => {
      try {
        const payload = buildPayload('png');
        const res = await fetch('/api/qr/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Error al generar previsualización');
        const data = await res.json();

        dom.qrPreviewImg.src = data.preview_url;
        dom.previewTargetUrl.textContent = data.raw_content.length > 80 
          ? data.raw_content.substring(0, 80) + '...' 
          : data.raw_content;

        dom.previewStatusText.textContent = 'QR Válido y Escaneable';
      } catch (err) {
        console.error(err);
        dom.previewStatusText.textContent = 'Error generando vista previa';
      } finally {
        dom.qrLoadingOverlay.classList.remove('active');
      }
    }, 250);
  }

  // ==========================================
  // GESTIÓN Y SUBIDA DE LOGOS
  // ==========================================
  function handleLogoFileSelect(e) {
    const file = e.target.files[0];
    if (file) uploadLogoFile(file);
  }

  async function uploadLogoFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      showToast('Subiendo logotipo...', 'info');
      const res = await fetch('/api/upload-logo', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Error al subir el logo');
      }

      const data = await res.json();
      state.logoPath = data.logo_path;
      updateLogoUI(data.logo_path);
      triggerLivePreview();
      loadAvailableLogos();
      showToast('¡Logotipo actualizado exitosamente!', 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function updateLogoUI(logoPath) {
    if (logoPath) {
      dom.logoPreviewBar.style.display = 'flex';
      dom.logoThumbImg.src = `/${logoPath}?t=${Date.now()}`;
      dom.logoNameLabel.textContent = logoPath;
      dom.logoStatusBadge.textContent = 'Logo Activo';
      dom.logoStatusBadge.style.display = 'inline-block';
    } else {
      dom.logoPreviewBar.style.display = 'none';
      dom.logoStatusBadge.style.display = 'none';
    }
  }

  async function loadAvailableLogos() {
    try {
      const res = await fetch('/api/logos');
      const data = await res.json();
      state.availableLogos = data.logos || [];

      dom.availableLogosGrid.innerHTML = '';
      state.availableLogos.forEach(logo => {
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = `quick-logo-pill ${state.logoPath === logo.path ? 'active' : ''}`;
        pill.innerHTML = `
          <img src="${logo.url}" alt="${logo.filename}">
          <span>${logo.filename}</span>
        `;
        pill.addEventListener('click', () => {
          state.logoPath = logo.path;
          updateLogoUI(logo.path);
          triggerLivePreview();
          document.querySelectorAll('.quick-logo-pill').forEach(p => p.classList.remove('active'));
          pill.classList.add('active');
          showToast(`Logo seleccionado: ${logo.filename}`, 'info');
        });
        dom.availableLogosGrid.appendChild(pill);
      });
    } catch (err) {
      console.warn('Error cargando logos guardados:', err);
    }
  }

  // ==========================================
  // DESCARGAS DE ARCHIVOS (PNG / SVG / ZIP)
  // ==========================================
  async function downloadFile(format) {
    try {
      showToast(`Generando archivo ${format.toUpperCase()} en alta definición...`, 'info');
      const payload = buildPayload(format);

      const res = await fetch('/api/qr/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Error al descargar el archivo QR');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${payload.filename || 'qr_codigo'}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();

      showToast(`¡Código QR (${format.toUpperCase()}) descargado con éxito!`, 'success');
    } catch (err) {
      showToast(`Error al descargar: ${err.message}`, 'error');
    }
  }

  async function downloadAllZip() {
    try {
      showToast('Empaquetando todas las tarjetas digitales en un archivo ZIP...', 'info');
      const a = document.createElement('a');
      a.href = '/api/qr/export-all';
      a.download = 'tarjetas_digitales_qr.zip';
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast('¡Descarga del archivo ZIP iniciada!', 'success');
    } catch (err) {
      showToast('Error al exportar el ZIP', 'error');
    }
  }

  // ==========================================
  // COPIAR IMAGEN AL PORTAPAPELES
  // ==========================================
  async function copyQrImageToClipboard() {
    try {
      if (!dom.qrPreviewImg.src) return;
      const res = await fetch(dom.qrPreviewImg.src);
      const blob = await res.blob();

      if (navigator.clipboard && window.ClipboardItem) {
        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob })
        ]);
        showToast('¡Imagen del QR copiada al portapapeles!', 'success');
      } else {
        showToast('Tu navegador no soporta copiado directo de imágenes', 'info');
      }
    } catch (err) {
      showToast('No se pudo copiar la imagen al portapapeles', 'error');
    }
  }

  // ==========================================
  // CATÁLOGO DE TARJETAS (CRUD)
  // ==========================================
  async function loadCatalog() {
    try {
      const res = await fetch('/api/tarjetas');
      const data = await res.json();
      state.cachedTarjetas = data.tarjetas || {};

      const count = Object.keys(state.cachedTarjetas).length;
      dom.cardsCountBadge.textContent = count;

      renderCatalogCards(state.cachedTarjetas);
    } catch (err) {
      console.error('Error al cargar catálogo:', err);
    }
  }

  function renderCatalogCards(cards) {
    dom.cardsCatalogGrid.innerHTML = '';
    const entries = Object.entries(cards);

    if (entries.length === 0) {
      dom.cardsCatalogGrid.innerHTML = `
        <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
          <p style="color: var(--text-muted); font-size: 1.1rem;">No hay tarjetas registradas aún.</p>
          <button class="btn btn-primary" style="margin-top: 1rem;" id="catalogCreateFirstBtn">Crear mi primera tarjeta</button>
        </div>
      `;
      document.getElementById('catalogCreateFirstBtn')?.addEventListener('click', () => {
        switchTab('designerSection');
      });
      return;
    }

    entries.forEach(([id, cardData]) => {
      const url = typeof cardData === 'object' ? cardData.url : cardData;
      const logo = typeof cardData === 'object' ? cardData.logo : '';
      const title = typeof cardData === 'object' && cardData.title ? cardData.title : id;

      const cardEl = document.createElement('div');
      cardEl.className = 'card-item';
      cardEl.dataset.id = id;
      cardEl.dataset.search = `${id} ${title} ${url}`.toLowerCase();

      cardEl.innerHTML = `
        <div class="card-item-preview">
          <img src="" alt="${title}" id="catalog_preview_${id}">
        </div>
        <div class="card-item-body">
          <h3 class="card-item-title">${escapeHtml(title)}</h3>
          <p class="card-item-url" title="${escapeHtml(url)}">${escapeHtml(url)}</p>
          <div class="card-item-meta">
            <span class="badge">${logo ? 'Con Logo' : 'Estándar'}</span>
            <span style="font-size: 0.75rem; color: var(--text-muted);">ID: ${escapeHtml(id)}</span>
          </div>
        </div>
        <div class="card-item-actions">
          <button class="btn btn-secondary btn-sm flex-1 edit-card-btn" data-id="${id}" title="Editar tarjeta">
            ✏️ Editar
          </button>
          <button class="btn btn-outline btn-sm download-card-btn" data-id="${id}" title="Descargar PNG">
            📥 PNG
          </button>
          <button class="btn btn-ghost btn-sm delete-card-btn" data-id="${id}" title="Eliminar">
            🗑️
          </button>
        </div>
      `;

      // Cargar preview asíncrono para la tarjeta
      loadCardThumbnail(id, url, logo);

      // Eventos de botones
      cardEl.querySelector('.edit-card-btn').addEventListener('click', () => loadCardIntoDesigner(id, cardData));
      cardEl.querySelector('.download-card-btn').addEventListener('click', () => downloadCardFromCatalog(id, url, logo));
      cardEl.querySelector('.delete-card-btn').addEventListener('click', () => deleteCardFromCatalog(id));

      dom.cardsCatalogGrid.appendChild(cardEl);
    });
  }

  async function loadCardThumbnail(id, url, logo) {
    try {
      const res = await fetch('/api/qr/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: url,
          logo_path: logo || null,
          box_size: 8,
          border: 2
        })
      });
      if (res.ok) {
        const data = await res.json();
        const img = document.getElementById(`catalog_preview_${id}`);
        if (img) img.src = data.preview_url;
      }
    } catch (e) {}
  }

  function filterCatalogCards() {
    const q = dom.cardsSearchInput.value.toLowerCase().trim();
    document.querySelectorAll('.card-item').forEach(el => {
      const text = el.dataset.search || '';
      el.style.display = text.includes(q) ? 'flex' : 'none';
    });
  }

  function loadCardIntoDesigner(id, cardData) {
    const url = typeof cardData === 'object' ? cardData.url : cardData;
    const logo = typeof cardData === 'object' ? cardData.logo : '';
    const title = typeof cardData === 'object' && cardData.title ? cardData.title : id;
    const fill = typeof cardData === 'object' && cardData.fill_color ? cardData.fill_color : '#000000';
    const back = typeof cardData === 'object' && cardData.back_color ? cardData.back_color : '#FFFFFF';

    dom.cardIdInput.value = id;
    dom.cardTitleInput.value = title;
    dom.urlInput.value = url;
    
    // Switch to URL type by default
    document.querySelector('.type-btn[data-type="url"]').click();

    state.fillColor = fill;
    state.backColor = back;
    dom.fillColorPicker.value = fill;
    dom.fillColorHex.value = fill;
    dom.backColorPicker.value = back;
    dom.backColorHex.value = back;

    state.logoPath = logo || null;
    updateLogoUI(state.logoPath);

    switchTab('designerSection');
    triggerLivePreview();
    showToast(`Tarjeta '${id}' cargada en el diseñador`, 'info');
  }

  async function downloadCardFromCatalog(id, url, logo) {
    try {
      showToast(`Generando PNG para '${id}'...`, 'info');
      const res = await fetch('/api/qr/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: url,
          logo_path: logo || null,
          format: 'png',
          filename: id
        })
      });
      const blob = await res.blob();
      const dlUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = dlUrl;
      a.download = `${id}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(dlUrl);
      a.remove();
      showToast(`¡${id}.png descargado!`, 'success');
    } catch (e) {
      showToast('Error al descargar tarjeta', 'error');
    }
  }

  async function saveCurrentCardToCatalog() {
    const cardId = dom.cardIdInput.value.trim();
    if (!cardId) {
      showToast('Debes ingresar un identificador para la tarjeta.', 'error');
      dom.cardIdInput.focus();
      return;
    }

    const payload = buildPayload('png');
    const targetUrl = payload.data || dom.previewTargetUrl.textContent;

    try {
      showToast('Guardando tarjeta en catálogo...', 'info');
      const res = await fetch('/api/tarjetas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: cardId,
          url: targetUrl,
          logo: state.logoPath || '',
          title: dom.cardTitleInput.value.trim() || cardId,
          fill_color: state.fillColor,
          back_color: state.backColor
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Error al guardar');
      }

      showToast(`¡Tarjeta '${cardId}' guardada en config.json!`, 'success');
      loadCatalog();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  }

  async function deleteCardFromCatalog(id) {
    if (!confirm(`¿Estás seguro de que deseas eliminar la tarjeta '${id}'?`)) return;

    try {
      const res = await fetch(`/api/tarjetas/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      });

      if (!res.ok) throw new Error('No se pudo eliminar la tarjeta');

      showToast(`Tarjeta '${id}' eliminada.`, 'success');
      loadCatalog();
    } catch (err) {
      showToast(`Error al eliminar: ${err.message}`, 'error');
    }
  }

  function resetToDefaultCard() {
    dom.cardIdInput.value = 'nueva_tarjeta';
    dom.cardTitleInput.value = 'Mi Nueva Tarjeta Digital';
    dom.urlInput.value = 'https://mi-tarjeta.digital';
    state.logoPath = null;
    updateLogoUI(null);
    triggerLivePreview();
  }

  // ==========================================
  // UTILIDADES Y TOASTS
  // ==========================================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    dom.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    })[m]);
  }

  // Arrancar app
  init();
});
