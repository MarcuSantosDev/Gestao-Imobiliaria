function parseMoedaBR(valor) {
    if (!valor) return null;
    const texto = valor.replace(/\s/g, '').replace('R$', '').replace(/\./g, '').replace(',', '.');
    const numero = Number(texto);
    return Number.isNaN(numero) ? null : numero;
}

function formatMoedaBR(valor) {
    if (valor === null || valor === undefined || valor === '') return '';
    return Number(valor).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function aplicarMascaraMoeda(input) {
    const formatar = () => {
        const numero = parseMoedaBR(input.value);
        if (numero !== null) {
            input.value = formatMoedaBR(numero);
        }
    };

    if (input.value) {
        const numero = parseMoedaBR(input.value) ?? Number(input.value);
        if (!Number.isNaN(numero)) {
            input.value = formatMoedaBR(numero);
        }
    }

    input.addEventListener('blur', formatar);
    input.addEventListener('change', formatar);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.moeda-input').forEach(aplicarMascaraMoeda);
});
