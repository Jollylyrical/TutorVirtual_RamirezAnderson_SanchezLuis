document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const sidebar = document.querySelector('#sidebar');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => document.body.classList.toggle('sidebar-open'));
    document.addEventListener('click', (event) => {
      if (!document.body.classList.contains('sidebar-open')) return;
      if (sidebar.contains(event.target) || menuToggle.contains(event.target)) return;
      document.body.classList.remove('sidebar-open');
    });
  }

  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const value = button.getAttribute('data-copy');
      try {
        await navigator.clipboard.writeText(value);
        const original = button.textContent;
        button.textContent = 'Copiado';
        setTimeout(() => { button.textContent = original; }, 1200);
      } catch (error) {
        button.textContent = value;
      }
    });
  });
});
