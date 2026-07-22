"""
Modul RPSManager untuk Pengelolaan Logika Bisnis Data RPS.

Modul ini mendefinisikan class RPSManager yang menjembatani Controller
dengan RPSRepository dan TextCleaner.
"""

from typing import List, Optional, Dict, Any
from models.rps import RPS
from repositories.rps_repository import RPSRepository
from utils.text_cleaner import TextCleaner
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RPSManager:
    """
    Manager class untuk logika bisnis pengelolaan RPS.
    """

    def __init__(self, rps_repo: RPSRepository, text_cleaner: TextCleaner) -> None:
        self.rps_repo: RPSRepository = rps_repo
        self.text_cleaner: TextCleaner = text_cleaner
        logger.info("RPSManager diinisialisasi.")

    def save_rps(self, rps_list: List[RPS], filename: str, filepath: str, filesize_kb: int) -> bool:
        """
        Menyimpan daftar RPS baru (hasil unggahan) secara massal dan transaksional.
        Sebelum disimpan, topik dibersihkan terlebih dahulu menggunakan TextCleaner.
        """
        if not rps_list:
            logger.warning("Daftar RPS kosong, tidak ada data untuk disimpan.")
            return False

        for rps in rps_list:
            raw_text = f"{rps.topic} {rps.sub_topic}".strip()
            rps.cleaned_topic = self.text_cleaner.clean_text(raw_text)

        logger.info(f"Memproses penyimpanan transaksional {len(rps_list)} record RPS.")
        return self.rps_repo.replace_all_rps(rps_list, filename, filepath, filesize_kb)

    def get_all_rps(self) -> List[RPS]:
        """
        Mengambil seluruh data RPS yang terdaftar.
        """
        return self.rps_repo.get_all()

    def get_rps_by_id(self, rps_id: int) -> Optional[RPS]:
        """
        Mengambil 1 data RPS berdasarkan ID.
        """
        return self.rps_repo.get_by_id(rps_id)

    def add_single_rps(self, rps: RPS) -> int:
        """
        Menambahkan 1 pertemuan RPS baru secara manual.
        """
        raw_text = f"{rps.topic} {rps.sub_topic}".strip()
        rps.cleaned_topic = self.text_cleaner.clean_text(raw_text)
        return self.rps_repo.create(rps)

    def update_rps(self, rps_id: int, data: Dict[str, Any]) -> bool:
        """
        Memperbarui topik/sub_topic data RPS berdasarkan ID.
        """
        existing = self.rps_repo.get_by_id(rps_id)
        if not existing:
            logger.error(f"Gagal memperbarui: RPS ID {rps_id} tidak ditemukan.")
            return False

        if "topic" in data:
            existing.topic = data["topic"]
        if "sub_topic" in data:
            existing.sub_topic = data["sub_topic"]

        raw_text = f"{existing.topic} {existing.sub_topic}".strip()
        existing.cleaned_topic = self.text_cleaner.clean_text(raw_text)

        return self.rps_repo.update(existing)

    def delete_rps(self, rps_id: int) -> bool:
        """
        Menghapus 1 data pertemuan RPS berdasarkan ID.
        """
        return self.rps_repo.delete(rps_id)
