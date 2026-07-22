DEFAULT_SIMILARITY_THRESHOLD = 0.8
ALLOWED_FILE_EXTENSIONS = {".pdf", "pdf"}

# ============================================================
# Status ENUM - harus IDENTIK dengan definisi MySQL ENUM:
# ENUM('SESUAI','TIDAK_SESUAI','TIDAK_DITEMUKAN','PENDING')
# ============================================================
STATUS_SESUAI = "SESUAI"
STATUS_TIDAK_SESUAI = "TIDAK_SESUAI"
STATUS_TIDAK_DITEMUKAN = "TIDAK_DITEMUKAN"
STATUS_PENDING = "PENDING"

MSG_VALIDATION_NO_DATA = "Data tidak ditemukan"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MSG_REPORT_FAILED = "Gagal membuat laporan"

# Stopwords Bahasa Indonesia untuk TextCleaner
STOPWORDS = frozenset({
    "dan", "yang", "untuk", "dengan", "atau", "dari", "ke", "di",
    "ini", "itu", "pada", "adalah", "dalam", "akan", "tidak", "juga",
    "sebagai", "oleh", "sudah", "saat", "setelah", "karena", "seperti",
    "antara", "ada", "masih", "tersebut", "telah", "yaitu", "bahwa",
    "secara", "lebih", "dapat", "bisa", "harus", "serta", "juga",
    "melalui", "terhadap", "setiap", "salah", "satu", "sama", "lain",
    "maupun", "atas", "bawah", "kiri", "kanan", "depan", "belakang",
    "sehingga", "namun", "tetapi", "namun", "kemudian", "selanjutnya",
    "pertama", "kedua", "ketiga", "keempat", "kelima", "ke",
    "pertemuan", "minggu", "kuliah", "materi", "pokok", "bahasan",
    "sub", "topik", "bab", "bagian", "modul"
})
