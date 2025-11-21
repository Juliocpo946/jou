from uuid import UUID
from datetime import datetime
from src.domain.entities.animal import Animal

class AnimalMapper:

    @staticmethod
    def from_db_row(row: tuple) -> Animal:
        return Animal(
            id=UUID(row[0]),
            ranch_id=UUID(row[1]),
            lot_id=UUID(row[2]) if row[2] else None,
            visual_tag=row[3],
            electronic_tag=row[4],
            name=row[5],
            sex=row[6],
            birth_date=row[7],
            breed=row[8],
            productive_status=row[9],
            reproductive_status=row[10],
            health_score=row[11],
            last_heat_date=row[12],
            last_birth_date=row[13],
            last_insemination_date=row[14],
            current_cluster_label=row[15],
            predicted_sale_date=row[16],
            expected_calving_date=row[17],
            suggested_dry_date=row[18],
            next_likely_heat_date=row[19],
            projected_weight_30d=float(row[20]) if row[20] else None,
            is_active=row[21],
            server_updated_at=row[22]
        )

    @staticmethod
    def from_dict(data: dict) -> Animal:
        return Animal(
            id=UUID(data.get("id")),
            ranch_id=UUID(data.get("ranch_id")),
            lot_id=UUID(data.get("lot_id")) if data.get("lot_id") else None,
            visual_tag=data.get("visual_tag"),
            electronic_tag=data.get("electronic_tag"),
            name=data.get("name"),
            sex=data.get("sex"),
            birth_date=data.get("birth_date"),
            breed=data.get("breed"),
            productive_status=data.get("productive_status"),
            reproductive_status=data.get("reproductive_status"),
            health_score=data.get("health_score", 100),
            last_heat_date=data.get("last_heat_date"),
            last_birth_date=data.get("last_birth_date"),
            last_insemination_date=data.get("last_insemination_date"),
            current_cluster_label=data.get("current_cluster_label", "PENDING"),
            predicted_sale_date=data.get("predicted_sale_date"),
            expected_calving_date=data.get("expected_calving_date"),
            suggested_dry_date=data.get("suggested_dry_date"),
            next_likely_heat_date=data.get("next_likely_heat_date"),
            projected_weight_30d=float(data.get("projected_weight_30d")) if data.get("projected_weight_30d") else None,
            is_active=data.get("is_active", True),
            server_updated_at=datetime.fromisoformat(data.get("server_updated_at", datetime.now().isoformat()))
        )