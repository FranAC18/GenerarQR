/**
 * QR Digital Studio - Frontend Application Engine (Vercel & Supabase Edition)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Estado global de la aplicación
  const state = {
    contentType: 'url',
    cardId: '',
    cardTitle: '',
    logoPath: 'img/kobaia.png',
    fillColor: '#000000',
    backColor: '#FFFFFF',
    logoSizeRatio: 0.22,
    border: 4,
    errorCorrection: 'H',
    isDynamic: true,
    cachedTarjetas: {},
    availableLogos: [],
    systemStatus: { mode: 'local', connected: false }
  };

  // Referencias al DOM
  const dom = {
    themeToggleBtn: document.getElementById('themeToggleBtn'),
    tabDesignerBtn: document.getElementById('tabDesignerBtn'),
    tabCatalogBtn: document.getElementById('tabCatalogBtn'),
    designerSection: document.getElementById('designerSection'),
    catalogSection: document.getElementById('catalogSection'),
    cardsCountBadge: document.getElementById('cardsCountBadge'),
    systemStatusBadge: document.getElementById('systemStatusBadge'),
    
    // Selectores de tipo
    typeBtns: document.querySelectorAll('.type-btn'),
    typeForms: document.querySelectorAll('.type-form'),
    isDynamicToggle: document.getElementById('isDynamicToggle'),
    dynamicToggleBox: document.querySelector('.dynamic-toggle-box'),
    qrModeBadge: document.getElementById('qrModeBadge'),

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
    logoStorageSource: document.getElementById('logoStorageSource'),
    removeLogoBtn: document.getElementById('removeLogoBtn'),
    logoStatusBadge: document.getElementById('logoStatusBadge'),

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
    saveBtnLabel: document.getElementById('saveBtnLabel'),
    downloadOptionsPanel: document.getElementById('downloadOptionsPanel'),
    testRedirectLinkBtn: document.getElementById('testRedirectLinkBtn'),
    copyImageBtn: document.getElementById('copyImageBtn'),
    exportZipTopBtn: document.getElementById('exportZipTopBtn'),
    exportAllZipBtn: document.getElementById('exportAllZipBtn'),
    newCardBtn: document.getElementById('newCardBtn'),

    // Catálogo
    cardsCatalogGrid: document.getElementById('cardsCatalogGrid'),
    cardsSearchInput: document.getElementById('cardsSearchInput'),
    toastContainer: document.getElementById('toastContainer'),

    // Barra de acciones móvil
    mobileActionsBar: document.getElementById('mobileActionsBar'),
    mobileDownloadPngBtn: document.getElementById('mobileDownloadPngBtn'),
    mobileSaveCatalogBtn: document.getElementById('mobileSaveCatalogBtn'),

    // Acordeones
    accordionHeaders: document.querySelectorAll('.accordion-header')
  };

  let debounceTimer = null;

  // ==========================================
  // INICIALIZACIÓN
  // ==========================================
  async function init() {
    initTheme();
    setupEventListeners();
    updateLogoUI(state.logoPath, 'local');
    await checkSystemStatus();
    loadCatalog();
    triggerLivePreview();
  }

  // ==========================================
  // ESTADO DEL SISTEMA (SUPABASE / LOCAL)
  // ==========================================
  async function checkSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        state.systemStatus = await res.json();
        if (state.systemStatus.mode === 'supabase') {
          dom.systemStatusBadge.className = 'status-pill supabase';
          dom.systemStatusBadge.innerHTML = '🟢 Supabase Cloud';
          dom.systemStatusBadge.title = 'Conectado a Supabase PostgreSQL y Storage';
        } else {
          dom.systemStatusBadge.className = 'status-pill local';
          dom.systemStatusBadge.innerHTML = '🟡 Modo Local';
          dom.systemStatusBadge.title = 'Usando config.json y almacenamiento local';
        }
      }
    } catch (e) {
      console.warn('No se pudo verificar estado del sistema:', e);
    }
  }

  // ==========================================
  // TEMA OSCURO / CLARO
  // ==========================================
  function initTheme() {
    const savedTheme = localStorage.getItem('qr_studio_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    syncThemeColor(savedTheme);
  }

  function syncThemeColor(theme) {
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
      meta.setAttribute('content', theme === 'dark' ? '#0b0f19' : '#f8fafc');
    });
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('qr_studio_theme', newTheme);
    syncThemeColor(newTheme);
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

    // En móvil la barra de acciones solo aplica al diseñador
    if (dom.mobileActionsBar) {
      dom.mobileActionsBar.classList.toggle('hidden', tabId !== 'designerSection');
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

    // Acordeones colapsables (menos scroll en móvil)
    dom.accordionHeaders.forEach(header => {
      header.addEventListener('click', () => {
        const section = header.closest('.accordion-section');
        const collapsed = section ? section.classList.toggle('collapsed') : false;
        header.setAttribute('aria-expanded', String(!collapsed));
      });
    });

    // Barra de acciones móvil
    dom.mobileDownloadPngBtn?.addEventListener('click', () => downloadFile('png'));
    dom.mobileSaveCatalogBtn?.addEventListener('click', saveCurrentCardToCatalog);

    function markAsUnsaved() {
      dom.downloadOptionsPanel?.classList.remove('active');
      dom.saveToCatalogBtn?.classList.remove('saved');
      if (dom.saveBtnLabel) dom.saveBtnLabel.textContent = 'Guardar y Generar Código QR';
    }

    // Dynamic QR Toggle
    dom.isDynamicToggle.addEventListener('change', (e) => {
      state.isDynamic = e.target.checked;
      if (state.isDynamic) {
        dom.qrModeBadge.textContent = '⚡ QR Dinámico';
        dom.qrModeBadge.style.background = 'rgba(245, 158, 11, 0.15)';
        dom.qrModeBadge.style.color = 'var(--warning)';
      } else {
        dom.qrModeBadge.textContent = '📌 QR Estático';
        dom.qrModeBadge.style.background = 'rgba(99, 102, 241, 0.15)';
        dom.qrModeBadge.style.color = 'var(--accent-primary)';
      }
      markAsUnsaved();
      triggerLivePreview();
    });

    // Área táctil ampliada: todo el cuadro conmuta el toggle
    dom.dynamicToggleBox?.addEventListener('click', (e) => {
      if (e.target.closest('a, button, input, label, .switch')) return;
      dom.isDynamicToggle.checked = !dom.isDynamicToggle.checked;
      dom.isDynamicToggle.dispatchEvent(new Event('change'));
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

        markAsUnsaved();
        triggerLivePreview();
      });
    });

    // Inputs reactivos
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
          markAsUnsaved();
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
        handleLogoFileSelect(files[0]);
      }
    });

    dom.removeLogoBtn.addEventListener('click', () => {
      state.pendingLogoFile = null;
      state.logoPath = null;
      updateLogoUI(null);
      markAsUnsaved();
      triggerLivePreview();
      showToast('Logotipo removido del QR', 'info');
    });

    // Botones de Descarga
    dom.downloadPngBtn?.addEventListener('click', () => downloadFile('png'));
    dom.downloadSvgBtn?.addEventListener('click', () => downloadFile('svg'));
    dom.exportZipTopBtn?.addEventListener('click', downloadAllZip);
    dom.exportAllZipBtn?.addEventListener('click', downloadAllZip);

    // Guardar en Catálogo (Botón Principal Grande)
    dom.saveToCatalogBtn?.addEventListener('click', saveCurrentCardToCatalog);

    // Probar Enlace de Redirección
    dom.testRedirectLinkBtn?.addEventListener('click', () => {
      const cardId = dom.cardIdInput.value.trim();
      if (!cardId) {
        showToast('Debes guardar la tarjeta antes de probar el enlace.', 'error');
        return;
      }
      const url = `/c/${encodeURIComponent(cardId)}`;
      window.open(url, '_blank');
    });

    // Copiar Imagen
    dom.copyImageBtn?.addEventListener('click', copyQrImageToClipboard);

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
      filename: cardId,
      is_dynamic: state.isDynamic
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
  // PREVISUALIZACIÓN EN TIEMPO REAL
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
        const userHasInput = Boolean(dom.urlInput.value.trim() || dom.cardIdInput.value.trim() || dom.vcardName.value.trim() || dom.waPhone.value.trim() || dom.wifiSsid.value.trim() || dom.textInput.value.trim());
        dom.previewTargetUrl.textContent = userHasInput ? data.raw_content : 'https://... (Escribe una URL o contenido)';
        dom.previewStatusText.textContent = state.isDynamic ? 'QR Dinámico Listo' : 'QR Estático Listo';
      } catch (err) {
        console.error(err);
        dom.previewStatusText.textContent = 'Error en previsualización';
      } finally {
        dom.qrLoadingOverlay.classList.remove('active');
      }
    }, 250);
  }

  // ==========================================
  // GESTIÓN DE LOGOTIPOS (PREVIEW LOCAL + SUBIDA AL GUARDAR)
  // ==========================================
  function handleLogoFileSelect(e) {
    const file = e.target.files ? e.target.files[0] : e;
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showToast('Por favor selecciona una imagen válida (PNG, JPG, SVG, WebP).', 'error');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target.result;
      state.pendingLogoFile = file;
      state.logoPath = dataUrl;
      state.logoFileName = file.name;

      updateLogoUI(dataUrl, 'Pendiente de guardar', dataUrl, file.name);
      markAsUnsaved();
      triggerLivePreview();
      showToast(`Logo '${file.name}' listo para la vista previa`, 'info');
    };
    reader.readAsDataURL(file);
  }

  function resolveLogoPreviewUrl(logoPath) {
    const rawPath = String(logoPath || '').trim();
    if (!rawPath) return '';

    if (/^(https?:|data:|blob:|\/\/)/i.test(rawPath)) {
      return rawPath;
    }

    const cleanPath = rawPath
      .replace(/\\/g, '/')
      .replace(/^\/+/, '')
      .split(/[?#]/, 1)[0];
    const assetPath = cleanPath.toLowerCase().startsWith('img/')
      ? cleanPath
      : `img/${cleanPath}`;

    return `/${assetPath}?v=${encodeURIComponent(assetPath)}-${Date.now()}`;
  }

  function updateLogoUI(logoPath, storage = null, previewUrl = null, customName = null) {
    if (logoPath) {
      dom.logoPreviewBar.style.display = 'flex';
      const rawPath = String(logoPath);
      const isRemote = /^(https?:|data:|blob:|\/\/)/i.test(rawPath);
      const isDataUri = rawPath.startsWith('data:');
      const fileNameOnly = customName || (isDataUri ? (state.logoFileName || 'logo_personalizado.png') : rawPath.split(/[?#]/, 1)[0].split('/').pop());
      const imageSource = previewUrl || rawPath;
      const imageUrl = /^(https?:|data:|blob:|\/\/)/i.test(imageSource)
        ? imageSource
        : resolveLogoPreviewUrl(imageSource);

      dom.logoThumbImg.classList.remove('is-broken');
      dom.logoThumbImg.closest('.logo-thumb-wrapper')?.classList.remove('is-broken');
      dom.logoThumbImg.alt = 'Logo actual';
      dom.logoThumbImg.onload = () => {
        dom.logoThumbImg.classList.remove('is-broken');
        dom.logoThumbImg.closest('.logo-thumb-wrapper')?.classList.remove('is-broken');
      };
      dom.logoThumbImg.onerror = () => {
        dom.logoThumbImg.classList.add('is-broken');
        dom.logoThumbImg.alt = '';
        dom.logoThumbImg.removeAttribute('src');
        dom.logoThumbImg.closest('.logo-thumb-wrapper')?.classList.add('is-broken');
      };
      dom.logoThumbImg.src = imageUrl;

      dom.logoNameLabel.textContent = fileNameOnly;
      dom.logoStorageSource.textContent = storage || (isRemote ? 'Supabase Storage' : 'Almacenamiento Local');
      dom.logoStatusBadge.textContent = 'Logo Activo';
      dom.logoStatusBadge.style.display = 'inline-block';
    } else {
      dom.logoPreviewBar.style.display = 'none';
      dom.logoStatusBadge.style.display = 'none';
      dom.logoThumbImg.removeAttribute('src');
      dom.logoThumbImg.closest('.logo-thumb-wrapper')?.classList.remove('is-broken');
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
  // CATÁLOGO DE TARJETAS (CRUD CON ANALÍTICAS)
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
      const isDynamic = typeof cardData === 'object' ? cardData.is_dynamic : true;
      const scanCount = typeof cardData === 'object' ? (cardData.scan_count || 0) : 0;

      const cardEl = document.createElement('div');
      cardEl.className = 'card-item';
      cardEl.dataset.id = id;
      cardEl.dataset.search = `${id} ${title} ${url}`.toLowerCase();

      cardEl.innerHTML = `
        <div class="card-item-preview">
          <img src="" alt="${title}" id="catalog_preview_${id}" loading="lazy" decoding="async">
        </div>
        <div class="card-item-body">
          <h3 class="card-item-title">${escapeHtml(title)}</h3>
          <p class="card-item-url" title="${escapeHtml(url)}">${escapeHtml(url)}</p>
          <div class="card-item-meta">
            <span class="scan-badge" title="Número de escaneos registrados">👁️ ${scanCount} escaneos</span>
            <span class="badge" style="font-size: 0.65rem;">${isDynamic ? '⚡ Dinámico' : '📌 Estático'}</span>
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

      // Cargar miniatura
      loadCardThumbnail(id, url, logo, isDynamic);

      // Eventos
      cardEl.querySelector('.edit-card-btn').addEventListener('click', () => loadCardIntoDesigner(id, cardData));
      cardEl.querySelector('.download-card-btn').addEventListener('click', () => downloadCardFromCatalog(id, url, logo, isDynamic));
      cardEl.querySelector('.delete-card-btn').addEventListener('click', () => deleteCardFromCatalog(id));

      dom.cardsCatalogGrid.appendChild(cardEl);
    });
  }

  async function loadCardThumbnail(id, url, logo, isDynamic) {
    try {
      const res = await fetch('/api/qr/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: url,
          logo_path: logo || null,
          filename: id,
          is_dynamic: isDynamic,
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
    const isDyn = typeof cardData === 'object' ? (cardData.is_dynamic ?? true) : true;

    dom.cardIdInput.value = id;
    dom.cardTitleInput.value = title;
    dom.urlInput.value = url;
    
    dom.isDynamicToggle.checked = isDyn;
    state.isDynamic = isDyn;

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

    // Activar panel de descargas al cargar una tarjeta ya guardada
    dom.downloadOptionsPanel?.classList.add('active');
    dom.saveToCatalogBtn?.classList.add('saved');
    if (dom.saveBtnLabel) dom.saveBtnLabel.textContent = '💾 Actualizar Tarjeta';

    switchTab('designerSection');
    triggerLivePreview();
    showToast(`Tarjeta '${id}' cargada en el diseñador`, 'info');
  }

  async function downloadCardFromCatalog(id, url, logo, isDynamic) {
    try {
      showToast(`Generando PNG para '${id}'...`, 'info');
      const res = await fetch('/api/qr/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: url,
          logo_path: logo || null,
          format: 'png',
          filename: id,
          is_dynamic: isDynamic
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
      showToast('Debes ingresar un identificador único (slug) para la tarjeta.', 'error');
      dom.cardIdInput.focus();
      return;
    }

    const payload = buildPayload('png');
    const targetUrl = payload.data || dom.previewTargetUrl.textContent;
    if (!targetUrl || targetUrl.includes('https://...')) {
      showToast('Ingresa una dirección URL o contenido para guardar la tarjeta.', 'error');
      dom.urlInput.focus();
      return;
    }

    try {
      showToast('Guardando tarjeta...', 'info');

      // Subir logotipo a almacenamiento ÚNICAMENTE ahora si hay un archivo nuevo cargado
      let targetLogoPath = state.logoPath || '';
      if (state.pendingLogoFile) {
        try {
          const formData = new FormData();
          formData.append('file', state.pendingLogoFile);
          const uploadRes = await fetch('/api/upload-logo', {
            method: 'POST',
            body: formData
          });
          if (uploadRes.ok) {
            const uploadData = await uploadRes.json();
            targetLogoPath = uploadData.logo_path;
            state.logoPath = targetLogoPath;
            state.pendingLogoFile = null;
            updateLogoUI(targetLogoPath, uploadData.storage, uploadData.url);
          }
        } catch (uploadErr) {
          console.warn('Advertencia al subir logo:', uploadErr);
        }
      }

      const res = await fetch('/api/tarjetas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: cardId,
          url: targetUrl,
          logo: targetLogoPath,
          title: dom.cardTitleInput.value.trim() || cardId,
          fill_color: state.fillColor,
          back_color: state.backColor,
          is_dynamic: state.isDynamic,
          content_type: state.contentType
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Error al guardar');
      }

      // Desplegar panel de opciones de descarga exclusivamente al guardar
      dom.downloadOptionsPanel?.classList.add('active');
      dom.saveToCatalogBtn?.classList.add('saved');
      if (dom.saveBtnLabel) dom.saveBtnLabel.textContent = 'Guardar Cambios';

      showToast(`¡Tarjeta '${cardId}' guardada con éxito!`, 'success');
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
    dom.cardIdInput.value = '';
    dom.cardTitleInput.value = '';
    dom.urlInput.value = '';
    dom.vcardName.value = '';
    dom.vcardPhone.value = '';
    dom.vcardOrg.value = '';
    dom.vcardTitle.value = '';
    dom.vcardEmail.value = '';
    dom.vcardUrl.value = '';
    dom.waPhone.value = '';
    dom.waMessage.value = '';
    dom.wifiSsid.value = '';
    dom.wifiPassword.value = '';
    dom.textInput.value = '';
    state.cardId = '';
    state.cardTitle = '';
    state.pendingLogoFile = null;
    state.logoPath = 'img/kobaia.png';
    updateLogoUI('img/kobaia.png');
    
    // Ocultar panel de descarga al crear nueva tarjeta hasta que se guarde
    dom.downloadOptionsPanel?.classList.remove('active');
    dom.saveToCatalogBtn?.classList.remove('saved');
    if (dom.saveBtnLabel) dom.saveBtnLabel.textContent = 'Guardar y Generar Código QR';

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
