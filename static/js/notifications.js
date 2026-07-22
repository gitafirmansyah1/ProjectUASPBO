// notifications.js - Helper functions for SweetAlert2 (v11)
// All functions return Promises where appropriate.

// Toast (top-end, 3s, fade, progress bar)
function showSuccess(message) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'success',
        title: 'Berhasil',
        text: message,
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        width: 300,
        didOpen: (toast) => {
            toast.style.transition = 'opacity 0.3s';
        }
    });
}

function showInfo(message) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: 'info',
        title: 'Informasi',
        text: message,
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        width: 300,
        didOpen: (toast) => {
            toast.style.transition = 'opacity 0.3s';
        }
    });
}

function showWarning(message) {
    Swal.fire({
        icon: 'warning',
        title: 'Peringatan',
        text: message,
        confirmButtonText: 'OK',
        backdrop: true,
        width: 400,
        customClass: {
            popup: 'swal2-border-radius'
        }
    });
}

function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Terjadi Kesalahan',
        text: message || 'Terjadi kesalahan pada sistem. Silakan coba kembali atau hubungi administrator.',
        confirmButtonText: 'OK',
        backdrop: true,
        width: 400,
        customClass: {
            popup: 'swal2-border-radius'
        }
    });
}

// Loading modal - call hideLoading() to close.
function showLoading(title = 'Memproses...') {
    Swal.fire({
        title: title,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
        customClass: {
            popup: 'swal2-border-radius'
        }
    });
}

function hideLoading() {
    Swal.close();
}

// Confirmation dialog - returns Promise<boolean>
function showConfirm(message, confirmText = 'Ya, Hapus', cancelText = 'Batal') {
    return Swal.fire({
        title: 'Konfirmasi',
        text: message,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: confirmText,
        cancelButtonText: cancelText,
        customClass: {
            popup: 'swal2-border-radius'
        }
    }).then(result => result.isConfirmed);
}
