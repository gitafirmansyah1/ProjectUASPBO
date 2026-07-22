"""
Modul BaseController untuk Arsitektur MVC Flask.

Modul ini mendefinisikan class BaseController yang menyediakan helper utilitas
seperti akses service, parsing request data, dan standardisasi JSON response.
"""

from flask import current_app, jsonify, Response
from typing import Any, Dict


class BaseController:
    """
    Kelas dasar (Base Class) untuk seluruh Web Controller.

    Menerapkan prinsip Inheritance untuk berbagi utilitas context, logger,
    dan parsing request dari Flask.
    """

    def get_service(self, name: str) -> Any:
        """
        Mengambil instansi service dari configuration context Flask.

        Args:
            name: Nama service yang ingin diambil (contoh: "rps_manager").

        Returns:
            Any: Objek service terkait.
        """
        services = current_app.config.get("SERVICES", {})
        service = services.get(name)
        if not service:
            raise KeyError(f"Service '{name}' tidak terdaftar pada aplikasi.")
        return service

    def json_response(self, data: Any, status_code: int = 200, message: str = None) -> Response:
        """
        Membentuk respon JSON terstandar untuk API.

        Struktur konsisten: { "success": true, "message": "...", "data": ... }

        Args:
            data: Data payload (dict, list, string, atau boolean).
            status_code: HTTP Status Code.
            message: Keterangan respon (opsional).

        Returns:
            Response: Respon Flask JSON.
        """
        msg = message
        payload_data = data

        if isinstance(data, dict):
            if "message" in data:
                if not msg:
                    msg = data["message"]
                if len(data) > 1:
                    payload_data = {k: v for k, v in data.items() if k != "message"}
                else:
                    payload_data = {}

        if not msg:
            msg = "Operasi berhasil." if status_code < 400 else "Operasi gagal."

        response_data = {
            "success": status_code < 400,
            "message": msg,
            "data": payload_data
        }

        return jsonify(response_data), status_code

    def json_error(self, message: str, status_code: int = 400, details: Dict[str, Any] = None) -> Response:
        """
        Membentuk respon JSON error terstandar.

        Args:
            message: Keterangan kesalahan.
            status_code: HTTP Status Code (>= 400).
            details: Informasi detail kesalahan tambahan (opsional).

        Returns:
            Response: Respon Flask JSON.
        """
        response_data = {
            "success": False,
            "message": message,
            "data": {},
            "details": details or {}
        }
        return jsonify(response_data), status_code