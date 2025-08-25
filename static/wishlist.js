// Handles wishlist toggle for dynamically loaded book cards

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('wishlist-btn')) {
            e.preventDefault();
            const btn = e.target;
            const bookId = btn.dataset.bookId;
            fetch('/api/toggle_wishlist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `book_id=${encodeURIComponent(bookId)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update button state instantly
                    btn.classList.toggle('btn-danger', data.in_wishlist);
                    btn.classList.toggle('btn-primary', !data.in_wishlist);
                    btn.textContent = data.in_wishlist ? '💔 Remove from Wishlist' : '❤️ Add to Wishlist';
                }
            });
        }
    });
});
