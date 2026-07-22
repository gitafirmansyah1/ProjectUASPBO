import os
from dataclasses import dataclass, field
from config.config import DatabaseConfig
from config.constants import DEFAULT_SIMILARITY_THRESHOLD

@dataclass
class AppSettings:
    db_config: DatabaseConfig = field(default_factory=DatabaseConfig)
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    upload_dir: str = os.environ.get("UPLOAD_DIR", "uploads")
    max_upload_size_mb: int = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 16))
    export_dir: str = os.environ.get("EXPORT_DIR", "exports")
