// JavaScript for dynamic book search on user dashboard

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="search"]');
    const filterSelect = document.querySelector('select[name="filter"]');
    const booksSection = document.querySelector('.section');

    if (!searchInput || !booksSection) return;

    let debounceTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(performSearch, 250);
    });
    if (filterSelect) {
        filterSelect.addEventListener('change', performSearch);
    }

    function performSearch() {
        const query = searchInput.value;
        const filter = filterSelect ? filterSelect.value : 'all';
        fetch(`/api/search_books?q=${encodeURIComponent(query)}&filter=${encodeURIComponent(filter)}`)
            .then(response => response.json())
            .then(books => {
                renderBooks(books, query);
            });
    }

    function renderBooks(books, query) {
        let html = `<h2>📚 ${query ? `Search Results for \"${query}\"` : 'Available Books'}</h2>`;
        if (books.length === 0) {
            html += `<p>No books found matching your search criteria. Try different keywords or filters.</p>`;
        } else {
            html += '<div class="books-grid">';
            books.forEach(book => {
                const availableCopies = book.total_stock - book.issued_count;
                const availabilityClass = availableCopies > 2 ? 'available' : (availableCopies > 0 ? 'limited' : 'unavailable');
                const availabilityText = availableCopies > 0 ? `Available (${availableCopies} copies)` : 'Not Available';
                    const wishlistBtnClass = book.in_wishlist ? 'btn-danger' : 'btn-primary';
                    const wishlistBtnText = book.in_wishlist ? '💔 Remove from Wishlist' : '❤️ Add to Wishlist';
                    html += `
                    <div class="book-card">
                        <div class="book-title">${escapeHtml(book.title)}</div>
                        <div class="book-author">by ${escapeHtml(book.author_name)}</div>
                        <div class="book-category">${escapeHtml(book.category)}</div>
                        <div class="book-details">${book.year ? `Published: ${escapeHtml(book.year)}<br>` : ''}</div>
                        <div class="book-availability"><span class="${availabilityClass}">${availabilityText}</span></div>
                        <div class="book-actions">
                            <button class="btn ${wishlistBtnClass} wishlist-btn" data-book-id="${book.book_id}">${wishlistBtnText}</button>
                        </div>
                    </div>`;
            });
            html += '</div>';
        }
        booksSection.innerHTML = html;
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
});
