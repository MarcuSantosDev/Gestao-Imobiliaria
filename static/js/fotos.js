function obterCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}

function atualizarContadorFotos(total) {
    document.querySelectorAll('[data-foto-contador]').forEach((el) => {
        el.textContent = `${total} foto${total === 1 ? '' : 's'}`;
    });
}

async function excluirFotoServidor(fotoId, deleteUrl) {
    const resp = await fetch(deleteUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': obterCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
    });
    if (!resp.ok) throw new Error('Falha ao excluir foto');
    return resp.json();
}

async function recortarFotoServidor(cropUrl, blob, fileName) {
    const formData = new FormData();
    formData.append('imagem', blob, fileName);
    const resp = await fetch(cropUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': obterCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
    });
    if (!resp.ok) throw new Error('Falha ao salvar recorte');
    return resp.json();
}

function urlAbsoluta(url) {
    try {
        return new URL(url, window.location.origin).href;
    } catch {
        return url;
    }
}

async function carregarImagemRemota(url) {
    const resp = await fetch(urlAbsoluta(url), {
        credentials: 'same-origin',
        cache: 'no-store',
    });
    if (!resp.ok) throw new Error('Falha ao carregar imagem');
    const blob = await resp.blob();
    if (!blob.type.startsWith('image/')) throw new Error('Arquivo inválido');
    return URL.createObjectURL(blob);
}

function revogarSrcRecorte(contexto) {
    if (contexto?.revogarSrc && contexto.src?.startsWith('blob:')) {
        URL.revokeObjectURL(contexto.src);
    }
}

let cropper = null;
let cropContext = null;
let modalRecorte = null;
let modalRecorteEl = null;

const CROPPER_OPCOES = {
    viewMode: 0,
    dragMode: 'crop',
    autoCropArea: 1,
    responsive: true,
    restore: false,
    background: false,
    checkOrientation: false,
    modal: false,
    guides: true,
    center: true,
    highlight: true,
    cropBoxMovable: true,
    cropBoxResizable: true,
    toggleDragModeOnDblclick: false,
};

function destruirCropper() {
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    const container = document.querySelector('.foto-crop-container');
    if (container) {
        container.innerHTML = '<img id="crop-image" alt="Recortar imagem">';
    }
}

function areaInteiraNatural(instancia) {
    const image = instancia.getImageData();
    return {
        x: 0,
        y: 0,
        width: image.naturalWidth,
        height: image.naturalHeight,
    };
}

function encaixarImagemInteira(instancia, cropData = null) {
    instancia.reset();
    instancia.resize();

    const container = instancia.getContainerData();
    const image = instancia.getImageData();
    if (!image.naturalWidth || !image.naturalHeight) return;

    const zoom = Math.min(
        container.width / image.naturalWidth,
        container.height / image.naturalHeight,
        1,
    );
    instancia.zoomTo(zoom);

    const area = cropData && cropData.width > 0 && cropData.height > 0
        ? cropData
        : areaInteiraNatural(instancia);
    instancia.setData(area);
}

function selecionarAreaInteira(instancia) {
    encaixarImagemInteira(instancia, areaInteiraNatural(instancia));
}

function obterCanvasRecortado(instancia) {
    const canvas = instancia.getCroppedCanvas({
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high',
    });
    if (!canvas || !canvas.width || !canvas.height) return null;

    const maxLado = 1920;
    const maiorLado = Math.max(canvas.width, canvas.height);
    if (maiorLado <= maxLado) return canvas;

    const escala = maxLado / maiorLado;
    const redimensionado = document.createElement('canvas');
    redimensionado.width = Math.round(canvas.width * escala);
    redimensionado.height = Math.round(canvas.height * escala);
    redimensionado.getContext('2d').drawImage(
        canvas, 0, 0, redimensionado.width, redimensionado.height,
    );
    return redimensionado;
}

function montarCropper(img) {
    cropper = new Cropper(img, {
        ...CROPPER_OPCOES,
        ready() {
            requestAnimationFrame(() => {
                if (!cropper) return;
                const cropData = cropContext?.tipo === 'preview' ? cropContext.cropData : null;
                encaixarImagemInteira(cropper, cropData);
            });
        },
    });
}

function aguardarImagem(img, src) {
    return new Promise((resolve, reject) => {
        const onLoad = () => {
            limpar();
            if (img.naturalWidth > 0) resolve();
            else reject(new Error('Imagem inválida'));
        };
        const onError = () => {
            limpar();
            reject(new Error('Imagem inválida'));
        };
        const limpar = () => {
            img.removeEventListener('load', onLoad);
            img.removeEventListener('error', onError);
        };
        img.addEventListener('load', onLoad);
        img.addEventListener('error', onError);
        img.src = src;
    });
}

async function iniciarCropperNoModal() {
    if (!cropContext?.src) return;

    destruirCropper();
    const img = document.getElementById('crop-image');
    if (!img) return;

    try {
        await aguardarImagem(img, cropContext.src);
        if (!cropContext) return;
        montarCropper(img);
    } catch (e) {
        alert('Não foi possível carregar a imagem para recorte.');
        modalRecorte?.hide();
    }
}

function criarModalRecorte() {
    if (modalRecorteEl) return;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="modal fade" id="modal-recorte-foto" tabindex="-1" aria-labelledby="modalRecorteFotoLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered modal-recorte-foto">
                <div class="modal-content">
                    <div class="modal-header py-2">
                        <h5 class="modal-title" id="modalRecorteFotoLabel">Recortar foto</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                    </div>
                    <div class="modal-body p-2">
                        <div class="foto-crop-container">
                            <img id="crop-image" alt="Recortar imagem">
                        </div>
                        <p class="text-muted small mb-0 mt-2">
                            A imagem original completa é exibida abaixo. Use a roda do mouse para zoom ou
                            <strong>Área inteira</strong> para voltar ao enquadramento original.
                        </p>
                    </div>
                    <div class="modal-footer py-2">
                        <button type="button" class="btn btn-outline-secondary btn-sm" id="btn-area-inteira-recorte">
                            <i class="bi bi-fullscreen"></i> Área inteira
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" id="btn-reset-zoom-recorte">
                            <i class="bi bi-arrows-angle-contract"></i> Ajustar à tela
                        </button>
                        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary btn-sm" id="btn-aplicar-recorte">Aplicar recorte</button>
                    </div>
                </div>
            </div>
        </div>`;
    document.body.appendChild(wrapper.firstElementChild);

    modalRecorteEl = document.getElementById('modal-recorte-foto');
    modalRecorte = new bootstrap.Modal(modalRecorteEl);

    modalRecorteEl.addEventListener('shown.bs.modal', () => {
        setTimeout(() => iniciarCropperNoModal(), 50);
    });

    modalRecorteEl.addEventListener('hidden.bs.modal', () => {
        destruirCropper();
        revogarSrcRecorte(cropContext);
        cropContext = null;
    });

    document.getElementById('btn-aplicar-recorte').addEventListener('click', aplicarRecorte);
    document.getElementById('btn-reset-zoom-recorte').addEventListener('click', () => {
        if (cropper) encaixarImagemInteira(cropper, cropper.getData(true));
    });
    document.getElementById('btn-area-inteira-recorte').addEventListener('click', () => {
        if (cropper) selecionarAreaInteira(cropper);
    });
}

function abrirRecorte(contexto) {
    if (typeof Cropper === 'undefined') {
        alert('Ferramenta de recorte não carregada. Recarregue a página.');
        return;
    }

    criarModalRecorte();

    if (modalRecorteEl.classList.contains('show')) {
        return;
    }

    revogarSrcRecorte(cropContext);
    destruirCropper();
    cropContext = contexto;
    modalRecorte.show();
}

function aplicarRecorte() {
    if (!cropper || !cropContext) return;

    const cropData = cropper.getData(true);
    const canvas = obterCanvasRecortado(cropper);

    if (!canvas) {
        alert('Não foi possível recortar esta imagem.');
        return;
    }

    const btn = document.getElementById('btn-aplicar-recorte');
    btn.disabled = true;

    canvas.toBlob(async (blob) => {
        try {
            if (cropContext.tipo === 'preview') {
                await cropContext.onAplicar(blob, cropData);
            } else if (cropContext.tipo === 'servidor') {
                const data = await recortarFotoServidor(
                    cropContext.cropUrl,
                    blob,
                    cropContext.fileName,
                );
                if (cropContext.imgElement) {
                    cropContext.imgElement.src = data.url;
                }
                if (cropContext.onAplicarServidor) {
                    cropContext.onAplicarServidor(data);
                }
            }
            modalRecorte.hide();
        } catch (e) {
            alert('Não foi possível salvar o recorte.');
        } finally {
            btn.disabled = false;
        }
    }, 'image/jpeg', 0.95);
}

function initExclusaoFotosServidor(container) {
    if (!container) return;

    container.addEventListener('click', async (event) => {
        const btnCrop = event.target.closest('[data-foto-crop-id]');
        if (btnCrop) {
            event.preventDefault();
            const card = btnCrop.closest('[data-foto-card]');
            const img = card?.querySelector('img');
            if (!img) return;

            const fotoId = btnCrop.dataset.fotoCropId;
            const urlImagem = btnCrop.dataset.originalSrc || img.src.split('?')[0];

            btnCrop.disabled = true;
            try {
                const blobUrl = await carregarImagemRemota(urlImagem);
                abrirRecorte({
                    tipo: 'servidor',
                    src: blobUrl,
                    revogarSrc: true,
                    cropUrl: btnCrop.dataset.cropUrl,
                    fileName: `foto_${fotoId}.jpg`,
                    imgElement: img,
                    onAplicarServidor: (data) => {
                        if (data.original_url) {
                            btnCrop.dataset.originalSrc = data.original_url.split('?')[0];
                        }
                    },
                });
            } catch (e) {
                alert('Não foi possível carregar a imagem para recorte.');
            } finally {
                btnCrop.disabled = false;
            }
            return;
        }

        const btn = event.target.closest('[data-foto-delete-id]');
        if (!btn) return;

        event.preventDefault();
        const card = btn.closest('[data-foto-card]');
        const fotoId = btn.dataset.fotoDeleteId;
        const deleteUrl = btn.dataset.deleteUrl;

        if (!confirm('Deseja excluir esta foto?')) return;

        btn.disabled = true;
        try {
            const data = await excluirFotoServidor(fotoId, deleteUrl);
            card.remove();
            atualizarContadorFotos(data.total_fotos);

            const grid = container.querySelector('[data-fotos-grid]');
            if (grid && !grid.children.length) {
                grid.remove();
            }
            if (!container.querySelector('[data-fotos-grid]') && !container.querySelector('[data-fotos-vazio]')) {
                const empty = document.createElement('div');
                empty.className = 'alert alert-light border';
                empty.dataset.fotosVazio = '';
                empty.textContent = 'Nenhuma foto cadastrada.';
                container.appendChild(empty);
            }
        } catch (e) {
            alert('Não foi possível excluir a foto.');
            btn.disabled = false;
        }
    });
}

function initPreviewNovasFotos(inputId, previewId, inputOriginalId) {
    const input = document.getElementById(inputId);
    const inputOriginal = document.getElementById(inputOriginalId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    /** @type {{ original: File, atual: File, cropData: object|null, urlOriginal: string, urlAtual: string|null }[]} */
    let fotosPreview = [];

    function revogarFoto(foto) {
        if (foto.urlOriginal) URL.revokeObjectURL(foto.urlOriginal);
        if (foto.urlAtual && foto.urlAtual !== foto.urlOriginal) {
            URL.revokeObjectURL(foto.urlAtual);
        }
    }

    function sincronizarInput() {
        const dt = new DataTransfer();
        const dtOriginal = new DataTransfer();
        fotosPreview.forEach((foto) => {
            dt.items.add(foto.atual);
            dtOriginal.items.add(foto.original);
        });
        input.files = dt.files;
        if (inputOriginal) inputOriginal.files = dtOriginal.files;
    }

    function renderPreview() {
        preview.innerHTML = '';
        if (!fotosPreview.length) {
            preview.classList.add('d-none');
            sincronizarInput();
            return;
        }

        preview.classList.remove('d-none');
        fotosPreview.forEach((foto, index) => {
            if (!foto.urlAtual) {
                foto.urlAtual = URL.createObjectURL(foto.atual);
            }

            const col = document.createElement('div');
            col.className = 'col-6 col-md-3 col-lg-2';
            col.dataset.previewIndex = index;
            col.innerHTML = `
                <div class="foto-card border border-success" data-foto-card>
                    <button type="button" class="foto-crop-btn" data-preview-crop="${index}" title="Recortar foto">
                        <i class="bi bi-crop"></i>
                    </button>
                    <button type="button" class="foto-delete-btn" data-preview-remove="${index}" title="Remover foto">&times;</button>
                    <img class="preview-img" alt="Nova foto ${index + 1}">
                    <div class="p-2">
                        <small class="text-success d-block">Nova foto ${index + 1}</small>
                        <small class="text-muted text-truncate d-block">${foto.atual.name}</small>
                    </div>
                </div>`;
            preview.appendChild(col);
            col.querySelector('.preview-img').src = foto.urlAtual;
        });

        sincronizarInput();
    }

    input.addEventListener('change', () => {
        const novos = Array.from(input.files || []);
        novos.forEach((arquivo) => {
            fotosPreview.push({
                original: arquivo,
                atual: arquivo,
                cropData: null,
                urlOriginal: URL.createObjectURL(arquivo),
                urlAtual: null,
            });
        });
        input.value = '';
        renderPreview();
    });

    preview.addEventListener('click', (event) => {
        const btnCrop = event.target.closest('[data-preview-crop]');
        if (btnCrop) {
            const index = Number(btnCrop.dataset.previewCrop);
            const foto = fotosPreview[index];
            if (!foto) return;

            abrirRecorte({
                tipo: 'preview',
                src: foto.urlOriginal,
                cropData: foto.cropData,
                fileName: foto.original.name.replace(/\.[^.]+$/, '') + '.jpg',
                onAplicar: async (blob, cropData) => {
                    const nome = foto.original.name.replace(/\.[^.]+$/, '') + '.jpg';
                    if (foto.urlAtual && foto.urlAtual !== foto.urlOriginal) {
                        URL.revokeObjectURL(foto.urlAtual);
                    }
                    foto.atual = new File([blob], nome, { type: 'image/jpeg' });
                    foto.cropData = cropData;
                    foto.urlAtual = URL.createObjectURL(foto.atual);
                    renderPreview();
                },
            });
            return;
        }

        const btn = event.target.closest('[data-preview-remove]');
        if (!btn) return;
        const index = Number(btn.dataset.previewRemove);
        revogarFoto(fotosPreview[index]);
        fotosPreview.splice(index, 1);
        renderPreview();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    criarModalRecorte();
    document.querySelectorAll('[data-fotos-servidor]').forEach(initExclusaoFotosServidor);
    initPreviewNovasFotos('input_novas_fotos', 'preview_novas_fotos', 'input_fotos_originais');
});
