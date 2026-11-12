// SkyHire Application Helper Scripts

document.addEventListener('DOMContentLoaded', function () {
    // Resume file upload drag and drop enhancement
    const dropZone = document.getElementById('drop-zone');
    const resumeInput = document.getElementById('resume-input');
    const chosenName = document.getElementById('file-chosen-name');

    if (dropZone && resumeInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                resumeInput.files = files;
                if (chosenName) {
                    chosenName.textContent = 'Selected: ' + files[0].name;
                    chosenName.classList.remove('hidden');
                }
            }
        }, false);
    }
});

// ==========================================
// JOB SHARING FUNCTIONALITY
// ==========================================

function getFullUrl(urlPath) {
    if (urlPath.startsWith('http://') || urlPath.startsWith('https://')) {
        return urlPath;
    }
    return window.location.origin + urlPath;
}

window.openShareModal = function (title, urlPath, department) {
    const fullUrl = getFullUrl(urlPath || window.location.pathname);
    const modal = document.getElementById('share-modal');
    if (!modal) return;

    // Populate modal content
    const titleEl = document.getElementById('share-modal-job-title');
    const deptEl = document.getElementById('share-modal-department');
    const inputEl = document.getElementById('share-modal-url-input');
    const linkedinBtn = document.getElementById('share-btn-linkedin');
    const twitterBtn = document.getElementById('share-btn-twitter');
    const whatsappBtn = document.getElementById('share-btn-whatsapp');
    const emailBtn = document.getElementById('share-btn-email');
    const nativeBtn = document.getElementById('share-btn-native');

    if (titleEl) titleEl.textContent = title;
    if (deptEl) deptEl.textContent = department || 'SkyHire Job Opening';
    if (inputEl) inputEl.value = fullUrl;

    const encodedUrl = encodeURIComponent(fullUrl);
    const encodedTitle = encodeURIComponent(title + ' at SkyHire');
    const shareText = encodeURIComponent(`Check out this open position for "${title}" on SkyHire!`);

    // Social URLs
    if (linkedinBtn) {
        linkedinBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;
    }
    if (twitterBtn) {
        twitterBtn.href = `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${shareText}`;
    }
    if (whatsappBtn) {
        whatsappBtn.href = `https://api.whatsapp.com/send?text=${shareText}%20${encodedUrl}`;
    }
    if (emailBtn) {
        emailBtn.href = `mailto:?subject=${encodedTitle}&body=${shareText}%0A%0AApply%20here:%20${encodedUrl}`;
    }

    // Native Web Share API (mobile / supported browsers)
    if (nativeBtn) {
        if (navigator.share) {
            nativeBtn.classList.remove('hidden');
            nativeBtn.onclick = function () {
                navigator.share({
                    title: title + ' - SkyHire',
                    text: `Check out this open position: ${title}`,
                    url: fullUrl
                }).catch(() => {});
            };
        } else {
            nativeBtn.classList.add('hidden');
        }
    }

    // Reset copy feedback
    const copyLabel = document.getElementById('share-copy-label');
    const copyIcon = document.getElementById('share-copy-icon');
    if (copyLabel) copyLabel.textContent = 'Copy';
    if (copyIcon) copyIcon.setAttribute('data-lucide', 'copy');
    if (window.lucide) window.lucide.createIcons();

    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
};

window.closeShareModal = function () {
    const modal = document.getElementById('share-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
};

window.copyModalShareLink = function () {
    const inputEl = document.getElementById('share-modal-url-input');
    const copyLabel = document.getElementById('share-copy-label');
    const copyIcon = document.getElementById('share-copy-icon');
    if (!inputEl) return;

    inputEl.select();
    inputEl.setSelectionRange(0, 99999); // Mobile support

    navigator.clipboard.writeText(inputEl.value).then(() => {
        if (copyLabel) copyLabel.textContent = 'Copied!';
        if (copyIcon) copyIcon.setAttribute('data-lucide', 'check');
        if (window.lucide) window.lucide.createIcons();
        showToast('Link copied to clipboard!');

        setTimeout(() => {
            if (copyLabel) copyLabel.textContent = 'Copy';
            if (copyIcon) copyIcon.setAttribute('data-lucide', 'copy');
            if (window.lucide) window.lucide.createIcons();
        }, 2500);
    }).catch(err => {
        // Fallback for older browsers
        document.execCommand('copy');
        if (copyLabel) copyLabel.textContent = 'Copied!';
        setTimeout(() => {
            if (copyLabel) copyLabel.textContent = 'Copy';
        }, 2500);
    });
};

window.quickShareJob = function (event, title, urlPath, department) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    window.openShareModal(title, urlPath, department);
};

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-xl shadow-lg text-xs font-semibold flex items-center space-x-2 transition-all transform duration-300 opacity-0 translate-y-2';
    toast.innerHTML = `<svg class="w-4 h-4 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('opacity-0', 'translate-y-2');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}


