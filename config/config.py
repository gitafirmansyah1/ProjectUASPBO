import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    host: str = os.environ.get("DB_HOST", "localhost")
    port: int = int(os.environ.get("DB_PORT", 3306))
    user: str = os.environ.get("DB_USER", "root")
    password: str = os.environ.get("DB_PASSWORD", "")
    database: str = os.environ.get("DB_NAME", "rps_bap_db")
    pool_name: str = "rps_bap_pool"
    pool_size: int = 5

    def get_connection_params(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
        }
