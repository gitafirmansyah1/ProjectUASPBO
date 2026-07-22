from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class RPS:
    meeting_number: int
    topic: str
    sub_topic: str = ""
    cleaned_topic: str = ""
    source_file: str = ""
    rps_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rps_id": self.rps_id,
            "meeting_number": self.meeting_number,
            "topic": self.topic,
            "sub_topic": self.sub_topic,
            "cleaned_topic": self.cleaned_topic,
            "source_file": self.source_file,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RPS":
        return cls(
            rps_id=data.get("rps_id"),
            meeting_number=data.get("meeting_number", 0),
            topic=data.get("topic", ""),
            sub_topic=data.get("sub_topic", ""),
            cleaned_topic=data.get("cleaned_topic", ""),
            source_file=data.get("source_file", "")
        )
