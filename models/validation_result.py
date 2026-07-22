"""
Modul Model ValidationResult untuk Sistem Validasi RPS-BAP.

Modul ini mendefinisikan entitas data ValidationResult yang merepresentasikan
hasil evaluasi kesesuaian antara materi RPS dan BAP untuk tiap pertemuan.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class ValidationResult:
    """
    Model entitas data ValidationResult.

    Attributes:
        meeting_number (int): Nomor pertemuan yang divalidasi.
        similarity_score (float): Skor kemiripan (0.00 - 100.00).
        status (str): Status hasil ('SESUAI', 'TIDAK_SESUAI', 'TIDAK_DITEMUKAN', 'PENDING').
        notes (str): Catatan penjelas hasil validasi.
        details (str): Catatan rincian hasil validasi.
        rps_id (Optional[int]): Foreign Key ke tabel rps.
        bap_id (Optional[int]): Foreign Key ke tabel bap.
        validation_id (Optional[int]): Primary Key ID database.
        rps_topic (str): Deskripsi topik RPS (untuk penyajian view).
        bap_material (str): Deskripsi materi BAP (untuk penyajian view).
        validated_at (Optional[Any]): Timestamp proses validasi.
    """
    meeting_number: int
    similarity_score: float
    status: str
    notes: str = ""
    details: str = ""
    rps_id: Optional[int] = None
    bap_id: Optional[int] = None
    validation_id: Optional[int] = None
    rps_topic: str = ""
    bap_material: str = ""
    validated_at: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Mengonversi objek ValidationResult menjadi dictionary untuk serialisasi JSON API.
        """
        val_date = ""
        if isinstance(self.validated_at, datetime):
            val_date = self.validated_at.strftime("%Y-%m-%d %H:%M:%S")
        elif self.validated_at:
            val_date = str(self.validated_at)

        note_text = self.notes or self.details or ""

        return {
            "validation_id": self.validation_id,
            "rps_id": self.rps_id,
            "bap_id": self.bap_id,
            "meeting_number": self.meeting_number,
            "similarity_score": float(self.similarity_score),
            "status": self.status,
            "notes": note_text,
            "details": note_text,
            "rps_topic": self.rps_topic,
            "bap_material": self.bap_material,
            "validated_at": val_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        """
        Membuat objek ValidationResult dari dictionary recordset database.
        """
        note_text = data.get("notes") or data.get("details") or ""
        score = float(data.get("similarity_score", 0.0))

        return cls(
            validation_id=data.get("validation_id"),
            rps_id=data.get("rps_id"),
            bap_id=data.get("bap_id"),
            meeting_number=data.get("meeting_number", 0),
            similarity_score=score,
            status=data.get("status", "PENDING"),
            notes=note_text,
            details=note_text,
            rps_topic=data.get("rps_topic", ""),
            bap_material=data.get("bap_material", ""),
            validated_at=data.get("validated_at")
        )
