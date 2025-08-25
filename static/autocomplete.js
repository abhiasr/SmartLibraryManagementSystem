// Autocomplete for search input

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    let acDropdown;
    let debounceTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            const q = searchInput.value.trim();
            if (q.length < 1) {
                closeDropdown();
                return;
            }
            fetch(`/api/search_suggestions?q=${encodeURIComponent(q)}`)
                .then(res => res.json())
                .then(suggestions => {
                    showDropdown(suggestions);
                });
        }, 200);
    });

    function showDropdown(suggestions) {
        closeDropdown();
        if (!suggestions.length) return;
        acDropdown = document.createElement('div');
        acDropdown.className = 'autocomplete-dropdown';
        suggestions.forEach(s => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = s;
            item.onclick = function() {
                searchInput.value = s;
                closeDropdown();
                searchInput.form && searchInput.form.dispatchEvent(new Event('submit'));
            };
            acDropdown.appendChild(item);
        });
        searchInput.parentNode.appendChild(acDropdown);
    }
    function closeDropdown() {
        if (acDropdown) acDropdown.remove();
        acDropdown = null;
    }
    document.addEventListener('click', function(e) {
        if (acDropdown && !acDropdown.contains(e.target) && e.target !== searchInput) {
            closeDropdown();
        }
    });
});
