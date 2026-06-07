(function () {
    const STORAGE_KEY = 'imobigest-theme';

    function getPreferredTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'light' || saved === 'dark') {
            return saved;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
    }

    function updateToggle() {
        const theme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
            }
            const label = theme === 'dark' ? 'Modo claro' : 'Modo noturno';
            btn.setAttribute('title', label);
            btn.setAttribute('aria-label', label);
        });
    }

    window.setTheme = function (theme) {
        localStorage.setItem(STORAGE_KEY, theme);
        applyTheme(theme);
        updateToggle();
    };

    window.toggleTheme = function () {
        const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
        setTheme(current === 'dark' ? 'light' : 'dark');
    };

    applyTheme(getPreferredTheme());
    document.addEventListener('DOMContentLoaded', updateToggle);
})();
