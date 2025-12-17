document.addEventListener('DOMContentLoaded', function() {
    initSourceManager();
    initConfirmDelete();
    initSidebarToggle();
});

function initSourceManager() {
    const addSourceBtn = document.getElementById('addSourceBtn');
    const sourcesContainer = document.getElementById('sourcesContainer');
    
    if (addSourceBtn && sourcesContainer) {
        addSourceBtn.addEventListener('click', function() {
            const sourceCount = sourcesContainer.querySelectorAll('.source-item').length;
            const sourceHtml = createSourceItem(sourceCount);
            sourcesContainer.insertAdjacentHTML('beforeend', sourceHtml);
        });
        
        sourcesContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-source')) {
                e.target.closest('.source-item').remove();
                updateSourceIndices();
            }
        });
    }
}

function createSourceItem(index) {
    return `
        <div class="source-item bg-gray-50 p-4 rounded-xl border border-gray-200">
            <div class="flex justify-between items-start mb-3">
                <span class="text-sm font-medium text-gray-600">Source ${index + 1}</span>
                <button type="button" class="remove-source text-red-500 hover:text-red-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label class="form-label">URL</label>
                    <input type="url" name="source_url_${index}" class="form-input" placeholder="https://...">
                </div>
                <div>
                    <label class="form-label">Type</label>
                    <select name="source_type_${index}" class="form-input">
                        <option value="rss">RSS Feed</option>
                        <option value="website">Website</option>
                    </select>
                </div>
            </div>
        </div>
    `;
}

function updateSourceIndices() {
    const sources = document.querySelectorAll('.source-item');
    sources.forEach((source, index) => {
        const label = source.querySelector('span');
        if (label) {
            label.textContent = `Source ${index + 1}`;
        }
        const urlInput = source.querySelector('input[type="url"]');
        const typeSelect = source.querySelector('select');
        if (urlInput) urlInput.name = `source_url_${index}`;
        if (typeSelect) typeSelect.name = `source_type_${index}`;
    });
}

function initConfirmDelete() {
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

function initSidebarToggle() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    
    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
        });
    }
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-xl shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, 3000);
}
