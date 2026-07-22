"""
Modul BAPManager untuk Pengelolaan Logika Bisnis Realisasi BAP.

Modul ini mendefinisikan class BAPManager yang bertindak sebagai service layer
antara Controller, BAPRepository, RPSRepository, dan TextCleaner.
Menjamin aturan bisnis BR-02 ter-evaluasi secara ketat.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from models.bap import BAP
from repositories.bap_repository import BAPRepository
from repositories.rps_repository import RPSRepository
from utils.text_cleaner import TextCleaner
from utils.exceptions import DuplicateMeetingError, MeetingNumberExceededError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BAPManager:
    """
    Manager class untuk logika bisnis pengelolaan BAP.
    """

    def __init__(
        self,
        bap_repo: BAPRepository,
        rps_repo: RPSRepository,
        text_cleaner: TextCleaner
    ) -> None:
        """
        Inisialisasi BAPManager dengan dependency injection.
        """
        self.bap_repo: BAPRepository = bap_repo
        self.rps_repo: RPSRepository = rps_repo
        self.text_cleaner: TextCleaner = text_cleaner
        logger.info("BAPManager diinisialisasi.")

    def get_all_bap(self) -> List[BAP]:
        """
        Mengambil seluruh data BAP yang terdaftar.
        """
        return self.bap_repo.get_all()

    def get_bap_by_id(self, bap_id: int) -> Optional[BAP]:
        """
        Mengambil 1 data BAP berdasarkan ID.
        """
        return self.bap_repo.get_by_id(bap_id)

    def get_total_rps_meetings(self) -> int:
        """
        Mendapatkan total jumlah pertemuan RPS yang terdaftar.
        """
        return self.rps_repo.count_all()

    def add_bap(self, bap: BAP) -> bool:
        """
        Menambahkan baris realisasi BAP baru dengan mengevaluasi Aturan Bisnis BR-02:
        1. DuplicateMeetingError jika nomor pertemuan BAP sudah terdaftar.
        2. MeetingNumberExceededError jika nomor pertemuan BAP melebihi total pertemuan RPS.
        """
        # 1. Evaluasi BR-02: Cek Duplikasi Pertemuan
        if self.bap_repo.exists(bap.meeting_number):
            logger.warning(f"Validasi BR-02 Gagal: Pertemuan ke-{bap.meeting_number} sudah ada.")
            raise DuplicateMeetingError(f"Pertemuan ke-{bap.meeting_number} sudah memiliki data realisasi BAP.")

        # 2. Evaluasi BR-02: Cek Batas Maksimal Pertemuan RPS
        total_rps = self.rps_repo.count_all()
        if total_rps > 0 and bap.meeting_number > total_rps:
            logger.warning(
                f"Validasi BR-02 Gagal: Pertemuan ke-{bap.meeting_number} melebihi batas RPS ({total_rps})."
            )
            raise MeetingNumberExceededError(
                f"Nomor pertemuan ({bap.meeting_number}) melebihi jumlah total pertemuan RPS yang terdaftar ({total_rps})."
            )

        # 3. Clean materi
        bap.cleaned_material = self.text_cleaner.clean(bap.material_taught)

        # 4. Simpan ke repository
        last_id = self.bap_repo.create(bap)
        return last_id > 0

    def update_bap(self, bap_id: int, data: Dict[str, Any]) -> bool:
        """
        Memperbarui data BAP berdasarkan ID.
        """
        existing = self.bap_repo.get_by_id(bap_id)
        if not existing:
            logger.error(f"Gagal memperbarui BAP: ID {bap_id} tidak ditemukan.")
            return False

        if "meeting_date" in data:
            m_date = data["meeting_date"]
            if isinstance(m_date, str) and m_date:
                try:
                    m_date = datetime.strptime(m_date, "%Y-%m-%d").date()
                except ValueError:
                    pass
            existing.meeting_date = m_date

        if "material_taught" in data:
            existing.material_taught = data["material_taught"]

        existing.cleaned_material = self.text_cleaner.clean(existing.material_taught)
        return self.bap_repo.update(existing)

    def delete_bap(self, bap_id: int) -> bool:
        """
        Menghapus 1 data BAP berdasarkan ID.
        """
        return self.bap_repo.delete(bap_id)
