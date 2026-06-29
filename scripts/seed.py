import os
import sys
from datetime import datetime, timezone
import random

from app.db.database import SessionLocal, engine, Base
from app.db.models import EvidenceRecord
from app.schemas.evidence import XAPIStatement


def seed_data():
  Base.metadata.create_all(bind=engine)
  db = SessionLocal()

  if db.query(EvidenceRecord).first():
      print("База данных уже содержит записи.")
      db.close()
      return

  statuses = ["pending", "reviewed", "rejected"]

  for i in range(1, 16):
      raw_data = {
            "actor": {"account": {"name": f"student_{random.randint(1, 5)}"}},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
            "object": {
                "id": f"http://github.com/org/repo/commit/mock_commit_{i}",
                "definition": {"type": "commit"}
            },
            "context": {"project": "Evidence Locker Test"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

      try:
          statement = XAPIStatement(**raw_data)
      except Exception as e:
          print(f"Ошибка валидации Pydantic {i}: {e}")
          continue
      
      status = random.choice(statuses)
      reviewed_by = "0" if status in ["reviewed", "rejected"] else "0"  # По ТЗ пока всегда 0
        
      db_record = EvidenceRecord(
          actor_id=statement.actor.account.name,
          source_system="seed_script",
          source_type=statement.object.definition.type,
          evidence_link=statement.object.id,
          context=str(statement.context),
          timestamp=statement.timestamp,
          review_status=status,
          reviewed_by=reviewed_by
      )
      db.add(db_record)

  db.commit()
  print("Генерация завершенна")
  db.close()

if __name__ == "__main__":
    seed_data()
