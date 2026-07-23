"""
Parser struktur RPS dari hasil ekstraksi PDF.

Modul ini hanya menangani normalisasi ringan dan pemisahan isi materi
menjadi topic dan sub_topic. Tidak ada business rule database di sini.
"""

import re
from typing import Dict, Iterable, List, Optional, Tuple


class RPSParser:
    """
    Helper untuk memetakan cell PDF RPS menjadi meeting_number, topic, sub_topic.
    """

    MEETING_HEADERS = ("pertemuan", "minggu", "sesi")
    MATERIAL_HEADERS = ("materi pembelajaran", "pokok bahasan", "bahan kajian", "topik")
    SUB_TOPIC_HEADERS = ("sub pokok", "sub bahasan", "sub-topik", "sub topik", "rincian materi")

    def normalize_cell(self, value: Optional[str], keep_newline: bool = True) -> str:
        """
        Normalisasi ringan: None ke string kosong, trim, rapikan spasi,
        dan buang newline berlebih.
        """
        if value is None:
            return ""
        text = str(value).replace("\r", "\n").replace("\t", " ")
        if keep_newline:
            lines = [re.sub(r"[ ]+", " ", line).strip() for line in text.split("\n")]
            return "\n".join(line for line in lines if line).strip()
        return re.sub(r"\s+", " ", text).strip()

    def normalize_multiline(self, value: Optional[str]) -> str:
        """
        Normalisasi multiline untuk preview dan penyimpanan sub_topic.
        """
        text = self.normalize_cell(value, keep_newline=True)
        return re.sub(r"\n{2,}", "\n", text).strip()

    def detect_columns(self, table: List[List[str]]) -> Tuple[int, int, int]:
        """
        Deteksi indeks kolom pertemuan, materi, dan sub pokok secara dinamis.
        """
        meeting_col = -1
        topic_col = -1
        sub_topic_col = -1

        header_rows = table[: min(8, len(table))]
        max_cols = max((len(row) for row in header_rows), default=0)

        for col_idx in range(max_cols):
            header_text = " ".join(
                self.normalize_cell(row[col_idx] if col_idx < len(row) else "", keep_newline=False).lower()
                for row in header_rows
            )
            if meeting_col == -1 and any(keyword in header_text for keyword in self.MEETING_HEADERS):
                meeting_col = col_idx
            if sub_topic_col == -1 and any(keyword in header_text for keyword in self.SUB_TOPIC_HEADERS):
                sub_topic_col = col_idx
            if topic_col == -1 and any(keyword in header_text for keyword in self.MATERIAL_HEADERS):
                topic_col = col_idx

        return meeting_col, topic_col, sub_topic_col

    def is_rps_table(self, table: List[List[str]]) -> bool:
        """
        Memastikan tabel punya ciri struktur RPS, bukan tabel identitas/pustaka.
        """
        if len(table) < 2:
            return False
        meeting_col, topic_col, _ = self.detect_columns(table)
        return meeting_col != -1 and topic_col != -1

    def split_topic_subtopic(self, material_text: str, explicit_sub_topic: str = "") -> Tuple[str, str]:
        """
        Memisahkan cell materi menjadi topic dan sub_topic.

        Jika satu cell berisi:
        Kontrak Kuliah
        Konsep dasar ...

        maka topic adalah baris pertama, dan sisanya menjadi sub_topic.
        Numbering/bullet tetap disimpan di sub_topic.
        """
        material = self.normalize_multiline(material_text)
        explicit_sub_topic = self.normalize_multiline(explicit_sub_topic)

        if not material:
            return "", explicit_sub_topic

        lines = [line for line in material.split("\n") if line.strip()]
        topic = lines[0].strip()
        sub_lines = lines[1:]

        if explicit_sub_topic:
            sub_lines.append(explicit_sub_topic)

        return self.normalize_cell(topic, keep_newline=False), self.normalize_multiline("\n".join(sub_lines))

    def append_sub_topic(self, current_sub_topic: str, continuation_text: str) -> str:
        """
        Menambahkan lanjutan cell PDF ke sub_topic pertemuan sebelumnya.
        """
        current = self.normalize_multiline(current_sub_topic)
        continuation = self.normalize_multiline(continuation_text)
        if not continuation:
            return current
        if not current:
            return continuation
        return self.normalize_multiline(f"{current}\n{continuation}")

    def rows_to_records(
        self,
        table: List[List[str]],
        meeting_col: int,
        topic_col: int,
        sub_topic_col: int = -1,
    ) -> List[Dict[str, str]]:
        """
        Mengubah baris tabel menjadi record RPS sementara.
        Mendukung row lanjutan yang tidak memiliki nomor pertemuan.
        """
        records: List[Dict[str, str]] = []
        current_record: Optional[Dict[str, str]] = None

        for row in table:
            if len(row) <= max(meeting_col, topic_col):
                continue

            meeting_text = self.normalize_cell(row[meeting_col], keep_newline=False)
            material_text = self.normalize_cell(row[topic_col], keep_newline=True)
            explicit_sub_topic = ""
            if sub_topic_col != -1 and len(row) > sub_topic_col:
                explicit_sub_topic = self.normalize_cell(row[sub_topic_col], keep_newline=True)

            meeting_number = self.extract_meeting_number(meeting_text)
            if meeting_number is None:
                if current_record and material_text:
                    current_record["sub_topic"] = self.append_sub_topic(
                        current_record.get("sub_topic", ""),
                        material_text,
                    )
                continue

            topic, sub_topic = self.split_topic_subtopic(material_text, explicit_sub_topic)
            if not topic:
                continue

            current_record = {
                "meeting_number": meeting_number,
                "topic": topic,
                "sub_topic": sub_topic,
            }
            records.append(current_record)

        return records

    def extract_meeting_number(self, value: str) -> Optional[int]:
        """
        Ekstrak nomor pertemuan dari angka biasa atau romawi.
        """
        text = self.normalize_cell(value, keep_newline=False).lower()
        if not text:
            return None

        match = re.search(r"\b(\d{1,2})\b", text)
        if match:
            return int(match.group(1))

        roman_map = {
            "xvi": 16, "xv": 15, "xiv": 14, "xiii": 13,
            "xii": 12, "xi": 11, "x": 10, "ix": 9,
            "viii": 8, "vii": 7, "vi": 6, "v": 5,
            "iv": 4, "iii": 3, "ii": 2, "i": 1,
        }
        for roman, number in roman_map.items():
            if re.search(rf"\b{roman}\b", text):
                return number
        return None

    def extract_mata_kuliah(self, raw_text: str, tables: Optional[List[List[List[str]]]] = None) -> str:
        """
        Mengekstrak nama mata kuliah dari isi dokumen PDF RPS.
        Mencari dari struktur tabel identitas, label Mata Kuliah, atau fallback regex.
        """
        # Tier 1: Periksa dari struktur tabel identitas jika tersedia
        if tables:
            for table in tables[:2]:
                for r_idx, row in enumerate(table):
                    row_cells = [self.normalize_cell(c, keep_newline=False) for c in row]
                    for c_idx, cell in enumerate(row_cells):
                        cell_upper = cell.upper()
                        if any(k in cell_upper for k in ["MATA KULIAH", "NAMA MATA KULIAH", "COURSE"]):
                            # Periksa baris berikutnya di kolom yang sama atau awal baris
                            for next_r in range(r_idx + 1, min(r_idx + 4, len(table))):
                                candidate_row = [self.normalize_cell(c, keep_newline=False) for c in table[next_r]]
                                for check_c in [c_idx, 0, 1]:
                                    if check_c < len(candidate_row):
                                        cand = candidate_row[check_c]
                                        if cand and cand.upper() not in ["KODE MK", "BOBOT", "SEMESTER", "(SKS)", "WK-1 BID.AKADEMIK"] and not cand.startswith("WK-"):
                                            cand_clean = re.sub(r"\s+[A-Z]{2,4}\s*\d+.*$", "", cand).strip()
                                            if len(cand_clean) >= 3:
                                                return cand_clean

        # Tier 2: Key-value regex (misal: "Mata Kuliah : Pemrograman Java Lanjut")
        m_kv = re.search(r"(?:MATA\s*KULIAH|Nama\s+Mata\s+Kuliah|Course)\s*[:\-]\s*([^\n\r]+)", raw_text or "", re.IGNORECASE)
        if m_kv:
            res = m_kv.group(1).strip()
            if len(res) >= 3 and res.upper() not in ["KODE MK", "BOBOT", "SEMESTER"]:
                return res

        # Tier 3: Pattern header tabel dalam teks mentah
        m_tbl = re.search(r"MATA\s*KULIAH[^\n]*\n+\s*([A-Za-z0-9\s\&\-\+]{3,60}?)(?=\s+[A-Z]{2,4}\s*\d+|\s+\d+\s+SKS|\s+\d+\s+\d+|\n)", raw_text or "", re.IGNORECASE)
        if m_tbl:
            res = m_tbl.group(1).strip()
            if len(res) >= 3 and not res.upper().startswith("KODE"):
                return res

        # Fallback jika tidak terdeteksi
        return "Belum Terdeteksi"
