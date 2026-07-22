"""
Modul Model Report untuk Sistem Validasi RPS-BAP.

Modul ini mendefinisikan entitas data Report yang menyajikan
ringkasan statistik dan daftar rincian hasil evaluasi pembelajaran.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Report:
    """
    Model entitas data Report.

    Attributes:
        compliance_percentage (float): Persentase kesesuaian (0.00 - 100.00).
        total_meetings (int): Total pertemuan perkuliahan.
        matched_count (int): Jumlah pertemuan berstatus SESUAI.
        valid_count (int): Alias jumlah pertemuan berstatus SESUAI.
        invalid_count (int): Jumlah pertemuan berstatus TIDAK_SESUAI.
        overall_percentage (float): Alias persentase kesesuaian.
        mismatched_list (List[Dict]): Daftar materi yang diacak / tidak sesuai.
        missing_list (List[Dict]): Daftar materi RPS yang belum diajarkan.
        results (List[Dict]): List rincian hasil validasi per pertemuan.
        items (List[Any]): Alias list hasil rincian validasi.
        generated_at (Optional[Any]): Timestamp pembuatan laporan.
    """
    compliance_percentage: float = 0.0
    total_meetings: int = 0
    matched_count: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    overall_percentage: float = 0.0
    mismatched_list: List[Dict[str, Any]] = field(default_factory=list)
    missing_list: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    items: List[Any] = field(default_factory=list)
    generated_at: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Mengonversi objek Report menjadi dictionary untuk serialisasi JSON API.
        """
        gen_str = ""
        if isinstance(self.generated_at, datetime):
            gen_str = self.generated_at.strftime("%Y-%m-%d %H:%M:%S")
        elif self.generated_at:
            gen_str = str(self.generated_at)

        perc = float(self.compliance_percentage or self.overall_percentage or 0.0)
        matched = self.matched_count or self.valid_count or 0
        res_items = self.results or self.items or []

        return {
            "compliance_percentage": perc,
            "overall_percentage": perc,
            "total_meetings": self.total_meetings,
            "matched_count": matched,
            "valid_count": matched,
            "invalid_count": self.invalid_count,
            "mismatched_list": self.mismatched_list or [],
            "missing_list": self.missing_list or [],
            "results": res_items,
            "items": res_items,
            "generated_at": gen_str,
        }
