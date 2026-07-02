import random
import uuid
from datetime import datetime, timezone

# Eсли запускаешь не из корня, а прямо из папки scripts
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.database import Base, SessionLocal, engine
from app.db.models import EvidenceRecord, ReviewStatus
from app.schemas.evidence import XAPIStatement


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(EvidenceRecord).first():
        print("База данных уже содержит записи")
        db.close()
        return

    statuses = [ReviewStatus.pending, ReviewStatus.reviewed, ReviewStatus.rejected]

    for i in range(1, 16):
        raw_data = {
            "id": str(uuid.uuid4()),
            "actor": {"account": {"name": f"student_{random.randint(1, 5)}"}},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
            "object": {
                "id": f"http://github.com/org/repo/commit/mock_commit_{i}",
                "definition": {"type": "commit"},
            },
            "context": {
                "project": f"project_{random.randint(1, 3)}",
                "extensions": {"source_system": "seed_script", "source_type": "commit"},
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            statement = XAPIStatement(**raw_data)
        except Exception as e:
            print(f"Ошибка валидации Pydantic для записи {i}: {e}")
            continue

        status = random.choice(statuses)

        db_record = EvidenceRecord(
            actor_id=statement.actor_id,
            verb_id=statement.verb.id,
            object_id=statement.object.id,
            timestamp=statement.timestamp,
            source_system=statement.source_system,
            source_type=statement.source_type,
            context_id=statement.context_id,
            note="Сгенерировано автоматически (Seed script)",
            raw_data=raw_data,
            review_status=status,
            reviewed_by="0",
        )
        db.add(db_record)

    db.commit()
    print("Успешно сгенерировано")
    db.close()


if __name__ == "__main__":
    seed_data()
