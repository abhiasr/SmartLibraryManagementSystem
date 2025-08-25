// Show More functionality for books grid

document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('booksGrid');
    const showMoreContainer = document.getElementById('showMoreContainer');
    if (!grid || !showMoreContainer) return;
    const allCards = Array.from(grid.children);
    const PAGE_SIZE = 10;
    let shown = 0;

    function renderPage() {
        allCards.forEach((card, idx) => {
            card.style.display = idx < shown ? '' : 'none';
        });
        if (shown < allCards.length) {
            showMoreContainer.innerHTML = '<button id="showMoreBtn" class="btn btn-secondary">Show More</button>';
            document.getElementById('showMoreBtn').onclick = function() {
                shown += PAGE_SIZE;
                renderPage();
            };
        } else {
            showMoreContainer.innerHTML = '';
        }
    }

    shown = PAGE_SIZE;
    renderPage();
});
