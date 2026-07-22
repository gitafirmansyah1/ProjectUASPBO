"""
Modul UploadController untuk Mengelola Proses Unggah dan Ekstraksi RPS.

Modul ini mendefinisikan class UploadController yang menangani upload dokumen PDF,
ekstraksi pokok bahasan, pratinjau data, dan penyimpanan permanen data RPS.

Sesuai PRD Single User & Single Course.
"""

import os
from flask import render_template, request, Response
from werkzeug.utils import secure_filename

from app.controllers.base_controller import BaseController
from services.file_upload_handler import FileUploadHandler
from services.pdf_extraction_service import PDFExtractionService
from services.rps_manager import RPSManager
from models.rps import RPS
from utils.logger import setup_logger

# Inisialisasi logger untuk controller
logger = setup_logger(__name__)


class UploadController(BaseController):
    """
    Controller untuk modul Unggah PDF RPS.
    """

    def index(self) -> str:
        """
        Menampilkan halaman form upload PDF RPS.

        Returns:
            str: HTML template hasil render.
        """
        return render_template("upload.html", active_page="upload")

    def upload_file(self) -> Response:
        """
        Menerima file PDF dari client, memproses penyimpanan, dan mengekstrak materi.

        Returns:
            Response: JSON API response berisi data pokok bahasan terekstrak.
        """
        print("STEP 1 Request diterima")
        logger.info("[STEP 1] Request upload file RPS PDF diterima.")
        
        if "file" not in request.files:
            logger.error(f"[STEP 2 FAILED] Field 'file' tidak ditemukan dalam request.files. Field tersedia: {list(request.files.keys())}")
            return self.json_error("Tidak ada file yang diunggah. Pastikan field bernama 'file'.")
            
        file = request.files["file"]
        if file.filename == "":
            logger.error("[STEP 2 FAILED] File ditemukan tetapi nama file kosong.")
            return self.json_error("Nama file kosong. Silakan pilih file PDF.")

        print("STEP 2 File ditemukan")
        logger.info(f"[STEP 2] File ditemukan: '{file.filename}'")

        upload_handler: FileUploadHandler = self.get_service("upload_handler")
        temp_dir = os.path.join(upload_handler.storage_path, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(temp_dir, filename)
        
        try:
            file.save(temp_file_path)
            
            # Simpan secara fisik dan catat log awal
            saved_path = upload_handler.save_file(temp_file_path)
            
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            print("STEP 3 File disimpan")
            logger.info(f"[STEP 3] File berhasil disimpan di path: {saved_path}")

            # Ekstrak data materi
            extraction_service: PDFExtractionService = self.get_service("extraction_service")
            try:
                extracted_data = extraction_service.extract_pokok_bahasan(saved_path)
                print("STEP 4 PDF dibaca")
                logger.info(f"[STEP 4] PDF berhasil dibaca dari: {saved_path}")
            except Exception as pdf_err:
                logger.error(f"[STEP 4 FAILED] PDFExtractionService gagal membaca file: {pdf_err}")
                return self.json_error(f"Gagal membaca PDF: {pdf_err}")
            
            if not extracted_data:
                logger.error("[STEP 5 FAILED] Data RPS gagal diekstrak: Tidak ada tabel atau baris pertemuan yang dapat terbaca.")
                return self.json_error("Gagal mengekstrak data: Tidak ada tabel/pertemuan terdeteksi pada dokumen PDF ini.")

            print("STEP 5 Data diekstrak")
            logger.info(f"[STEP 5] Data RPS berhasil diekstrak. Total {len(extracted_data)} pertemuan terdeteksi.")
            
            print("STEP 8 Response JSON")
            logger.info("[STEP 8] Response JSON hasil ekstraksi berhasil dikirim.")
            return self.json_response(
                {
                    "source_file": os.path.basename(saved_path),
                    "items": extracted_data
                },
                message="Upload berhasil."
            )
            
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            logger.exception(f"[UPLOAD PROCESS FAILED] Kesalahan internal saat mengunggah & mengekstrak file PDF: {e}")
            return self.json_error(f"Terjadi kesalahan saat memproses file PDF: {e}")

    def save_extracted_rps(self) -> Response:
        """
        Menyimpan data hasil ekstraksi yang disetujui pengguna ke database secara permanen.
        """
        print("STEP 1 Request diterima (SAVE)")
        logger.info("[STEP 1 - SAVE] Request penyimpanan permanen hasil ekstraksi RPS diterima.")
        payload = request.get_json()
        if not payload:
            logger.error("[STEP 6 FAILED] Payload JSON kosong.")
            return self.json_error("Payload data kosong.")

        source_file = payload.get("source_file", "Upload Web")
        items = payload.get("items", [])

        if not items:
            logger.error("[STEP 6 FAILED] Tidak ada item data pertemuan untuk disimpan.")
            return self.json_error("Tidak ada item data pertemuan untuk disimpan.")

        print("STEP 6 Data divalidasi")
        logger.info(f"[STEP 6] Data berhasil divalidasi ({len(items)} item RPS siap disimpan).")

        upload_handler: FileUploadHandler = self.get_service("upload_handler")
        filepath = os.path.join(upload_handler.storage_path, source_file)
        filesize_kb = int(os.path.getsize(filepath) / 1024) if os.path.exists(filepath) else 0

        # Konversi data ke objek model RPS
        rps_list = []
        for i in items:
            rps_list.append(
                RPS(
                    meeting_number=int(i["meeting_number"]),
                    topic=i["topic"],
                    sub_topic=i.get("sub_topic", ""),
                    source_file=source_file
                )
            )

        try:
            # Simpan massal transaksional terpadu (mengganti data lama)
            rps_manager: RPSManager = self.get_service("rps_manager")
            success = rps_manager.save_rps(rps_list, source_file, filepath, filesize_kb)
            if success:
                print("STEP 7 INSERT database")
                logger.info(f"[STEP 7] INSERT database berhasil ({len(rps_list)} record RPS tersimpan).")
                print("STEP 8 Response JSON")
                logger.info("[STEP 8] Response JSON simpan RPS berhasil dikirim.")
                return self.json_response(
                    {"message": f"Berhasil menyimpan {len(rps_list)} pertemuan RPS."},
                    message=f"Berhasil menyimpan {len(rps_list)} pertemuan RPS."
                )
            else:
                logger.error("[STEP 7 FAILED] RPSManager/Repository gagal melakukan transaksi INSERT ke database.")
                return self.json_error("Gagal menulis data ke database.")
        except Exception as e:
            logger.exception(f"[STEP 7 FAILED] Repository gagal INSERT karena kesalahan database: {e}")
            return self.json_error(f"Kesalahan penyimpanan database: {e}")