import logging
import time

from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import Item
from app.seed.items import DEMO_ITEMS

logger = logging.getLogger(__name__)


def init_db() -> None:
    settings = get_settings()
    for attempt in range(1, 16):
        try:
            Base.metadata.create_all(bind=engine)
            migrate_db()
            if settings.seed_demo_data:
                with Session(engine) as db:
                    seed_items(db)
            return
        except OperationalError:
            logger.info("Database is not ready yet, retry %s/15", attempt)
            time.sleep(2)
    Base.metadata.create_all(bind=engine)


def migrate_db() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "premium_until" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN premium_until TIMESTAMP NULL"))


def seed_items(db: Session) -> None:
    count = db.scalar(select(func.count(Item.id))) or 0
    if count:
        return
    db.add_all(Item(**item) for item in DEMO_ITEMS)
    db.commit()
    logger.info("Seeded %s demo items", len(DEMO_ITEMS))
