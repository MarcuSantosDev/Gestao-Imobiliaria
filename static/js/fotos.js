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

function initExclusaoFotosServidor(container) {
    if (!container) return;

    container.addEventListener('click', async (event) => {
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

function initPreviewNovasFotos(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    let arquivosSelecionados = [];

    function renderPreview() {
        preview.innerHTML = '';
        if (!arquivosSelecionados.length) {
            preview.classList.add('d-none');
            return;
        }

        preview.classList.remove('d-none');
        arquivosSelecionados.forEach((arquivo, index) => {
            const col = document.createElement('div');
            col.className = 'col-6 col-md-3 col-lg-2';
            col.dataset.previewIndex = index;
            col.innerHTML = `
                <div class="foto-card border border-success" data-foto-card>
                    <button type="button" class="foto-delete-btn" data-preview-remove="${index}" title="Remover foto">&times;</button>
                    <img class="preview-img" alt="Nova foto ${index + 1}">
                    <div class="p-2">
                        <small class="text-success d-block">Nova foto ${index + 1}</small>
                        <small class="text-muted text-truncate d-block">${arquivo.name}</small>
                    </div>
                </div>`;
            preview.appendChild(col);
            col.querySelector('.preview-img').src = URL.createObjectURL(arquivo);
        });

        sincronizarInput();
    }

    function sincronizarInput() {
        const dt = new DataTransfer();
        arquivosSelecionados.forEach((arquivo) => dt.items.add(arquivo));
        input.files = dt.files;
    }

    input.addEventListener('change', () => {
        const novos = Array.from(input.files || []);
        arquivosSelecionados = arquivosSelecionados.concat(novos);
        input.value = '';
        renderPreview();
    });

    preview.addEventListener('click', (event) => {
        const btn = event.target.closest('[data-preview-remove]');
        if (!btn) return;
        const index = Number(btn.dataset.previewRemove);
        arquivosSelecionados.splice(index, 1);
        renderPreview();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-fotos-servidor]').forEach(initExclusaoFotosServidor);
    initPreviewNovasFotos('input_novas_fotos', 'preview_novas_fotos');
});
