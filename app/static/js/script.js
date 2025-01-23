// static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('mainForm');
    const previewModal = new bootstrap.Modal('#previewModal');
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
    `;
    document.body.appendChild(loadingOverlay);

    // Update color previews
    function updateColorPreviews() {
        document.querySelectorAll('.color-input').forEach(input => {
            const target = document.querySelector(`.color-preview[data-target="${input.name}"]`);
            if (target) {
                target.style.backgroundColor = input.value;
            }
        });
    }

    // Handle preview generation
    document.getElementById('previewButton').addEventListener('click', async () => {
        previewModal.show();
        updatePreviewImage();
    });

    // Update preview image
    document.getElementById('updatePreview').addEventListener('click', updatePreviewImage);

    async function updatePreviewImage() {
        const formData = new FormData(form);
        formData.append('preview_digit', document.getElementById('previewDigit').value);

        try {
            const response = await fetch('/preview', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            document.getElementById('previewImage').src = url;
        } catch (error) {
            alert(`Preview error: ${error.message}`);
        }
    }

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingOverlay.style.display = 'flex';

        try {
            const formData = new FormData(form);
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `digits_${Date.now()}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            alert(`Generation error: ${error.message}`);
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    // Initial color preview update
    updateColorPreviews();
    document.querySelectorAll('.color-input').forEach(input => {
        input.addEventListener('input', updateColorPreviews);
    });
});
