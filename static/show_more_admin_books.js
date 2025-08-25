// Show More functionality for admin books table

document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('.table-container table');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const allRows = Array.from(tbody.children);
    const PAGE_SIZE = 10;
    let shown = 0;

    function renderPage() {
        allRows.forEach((row, idx) => {
            row.style.display = idx < shown ? '' : 'none';
        });
        let showMoreBtn = document.getElementById('showMoreAdminBtn');
        if (shown < allRows.length) {
            if (!showMoreBtn) {
                showMoreBtn = document.createElement('button');
                showMoreBtn.id = 'showMoreAdminBtn';
                showMoreBtn.className = 'btn btn-secondary';
                showMoreBtn.textContent = 'Show More';
                table.parentNode.appendChild(showMoreBtn);
            }
            showMoreBtn.onclick = function() {
                shown += PAGE_SIZE;
                renderPage();
            };
        } else if (showMoreBtn) {
            showMoreBtn.remove();
        }
    }

    shown = PAGE_SIZE;
    renderPage();
});
