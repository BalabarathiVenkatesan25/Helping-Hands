document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark Mode / Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;
    
    // Check local storage for theme preference
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('theme', target);
            updateThemeIcon(target);
            showToast(`Theme switched to ${target} mode!`, 'info');
        });
    }

    function updateThemeIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'fa-solid fa-sun';
        } else {
            themeIcon.className = 'fa-solid fa-moon';
        }
    }

    // 2. Notification Drawer Toggle
    const notifBell = document.getElementById('notif-bell');
    const notifDrawer = document.getElementById('notif-drawer');

    if (notifBell && notifDrawer) {
        notifBell.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDrawer.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!notifDrawer.contains(e.target) && e.target !== notifBell) {
                notifDrawer.classList.remove('show');
            }
        });
    }

    // 3. Mark Single Notification as Read
    const notifItems = document.querySelectorAll('.notif-drawer-item');
    notifItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const notifId = this.dataset.id;
            if (!notifId) return;

            fetch(`/notifications/mark-read/${notifId}/`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update badge count
                    const badge = document.querySelector('.notif-badge');
                    if (badge) {
                        if (data.unread_count > 0) {
                            badge.textContent = data.unread_count;
                        } else {
                            badge.remove();
                        }
                    }
                    // Remove this item from list
                    this.remove();
                    showToast("Notification marked as read.", "success");
                }
            })
            .catch(err => console.error(err));
        });
    });

    // Mark All Notifications as Read
    const markAllBtn = document.getElementById('mark-all-read');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', (e) => {
            e.preventDefault();
            fetch('/notifications/mark-read/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const badge = document.querySelector('.notif-badge');
                    if (badge) badge.remove();
                    
                    const drawerContent = document.querySelector('.notif-drawer-content');
                    if (drawerContent) {
                        drawerContent.innerHTML = '<div class="p-3 text-center text-muted">No new notifications</div>';
                    }
                    showToast("All notifications marked as read.", "success");
                }
            })
            .catch(err => console.error(err));
        });
    }

    // 4. AJAX Live Search and Filter
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        const inputs = searchForm.querySelectorAll('input, select');
        
        let debounceTimer;
        inputs.forEach(input => {
            // Determine trigger event
            const eventType = input.tagName === 'SELECT' ? 'change' : 'keyup';
            
            input.addEventListener(eventType, () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    performSearch();
                }, 300);
            });
        });
    }

    function performSearch() {
        const searchForm = document.getElementById('search-form');
        if (!searchForm) return;

        const formData = new FormData(searchForm);
        const params = new URLSearchParams(formData).toString();
        const endpoint = searchForm.dataset.endpoint;
        const targetContainer = document.getElementById(searchForm.dataset.target);

        if (!endpoint || !targetContainer) return;

        // Visual feedback
        targetContainer.style.opacity = '0.5';

        fetch(`${endpoint}?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            targetContainer.innerHTML = data.html;
            targetContainer.style.opacity = '1';
            
            // Re-bind click listeners for dynamically loaded content (e.g. Favorite toggles)
            bindFavoriteToggles();
        })
        .catch(err => {
            console.error(err);
            targetContainer.style.opacity = '1';
        });
    }

    // 5. AJAX Toggle Favorite Orphanages
    function bindFavoriteToggles() {
        const favButtons = document.querySelectorAll('.btn-favorite');
        favButtons.forEach(btn => {
            // Remove old listener to prevent duplicates
            btn.replaceWith(btn.cloneNode(true));
        });

        // Query again and bind fresh listeners
        const freshButtons = document.querySelectorAll('.btn-favorite');
        freshButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const orphanageId = this.dataset.id;
                if (!orphanageId) return;

                fetch(`/donations/orphanages/${orphanageId}/toggle-favorite/`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(res => {
                    if (res.status === 403) {
                        showToast("Please log in as a Donor to save favorites.", "error");
                        return;
                    }
                    return res.json();
                })
                .then(data => {
                    if (!data) return;
                    
                    const icon = this.querySelector('i');
                    if (data.is_favorited) {
                        icon.className = 'fa-solid fa-star';
                        this.classList.add('active');
                        showToast(data.message, 'success');
                    } else {
                        icon.className = 'fa-regular fa-star';
                        this.classList.remove('active');
                        showToast(data.message, 'warning');
                    }
                })
                .catch(err => console.error(err));
            });
        });
    }
    
    // Bind initially
    bindFavoriteToggles();
});

// 6. Custom Toast Notification Manager
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-xmark';
    if (type === 'warning') iconClass = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Fade out and remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse forwards';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// 7. SweetAlert Confirmations Wrapper
function confirmAction(url, title = "Are you sure?", text = "You will not be able to undo this action!", confirmText = "Yes, proceed!") {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4f46e5',
            cancelButtonColor: '#64748b',
            confirmButtonText: confirmText
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = url;
            }
        });
    } else {
        if (confirm(`${title}\n${text}`)) {
            window.location.href = url;
        }
    }
}
