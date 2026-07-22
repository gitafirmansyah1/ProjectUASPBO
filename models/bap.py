from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date, datetime

@dataclass
class BAP:
    meeting_number: int
    meeting_date: Any
    material_taught: str
    cleaned_material: str = ""
    bap_id: Optional[int] = None

    @property
    def material_realization(self) -> str:
        return self.material_taught

    @material_realization.setter
    def material_realization(self, value: str) -> None:
        self.material_taught = value

    def to_dict(self) -> Dict[str, Any]:
        date_str = ""
        if isinstance(self.meeting_date, (date, datetime)):
            date_str = self.meeting_date.strftime("%Y-%m-%d")
        elif self.meeting_date:
            date_str = str(self.meeting_date)

        return {
            "bap_id": self.bap_id,
            "meeting_number": self.meeting_number,
            "meeting_date": date_str,
            "material_taught": self.material_taught,
            "material_realization": self.material_taught,
            "cleaned_material": self.cleaned_material,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BAP":
        meeting_date_val = data.get("meeting_date")
        if isinstance(meeting_date_val, str) and meeting_date_val:
            try:
                meeting_date_val = datetime.strptime(meeting_date_val, "%Y-%m-%d").date()
            except ValueError:
                pass

        material = data.get("material_taught") or data.get("material_realization") or ""

        return cls(
            bap_id=data.get("bap_id"),
            meeting_number=data.get("meeting_number", 0),
            meeting_date=meeting_date_val,
            material_taught=material,
            cleaned_material=data.get("cleaned_material", "")
        )
