"""Add or resume one synthetic dataset without credentials or destructive resets."""

import argparse
import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionFactory, close_engine
from app.ml.runtime import ml_runtime
from app.models.security_event import SecurityEvent
from app.services.demo import DEMO_SOURCE, demo_events, require_development
from app.services.ingestion import IngestionService


async def seed() -> None:
    settings = get_settings()
    require_development(settings.environment)
    if settings.brute_force_threshold != 10 or settings.api_volume_threshold != 30:
        raise ValueError("Portfolio demo requires the default detection thresholds")
    if settings.ml_enabled:
        ml_runtime.load(settings.ml_model_path)
    async with SessionFactory() as session:
        existing = list(
            await session.scalars(select(SecurityEvent).where(SecurityEvent.source == DEMO_SOURCE))
        )
        indexes = {int(event.event_metadata["seed_index"]) for event in existing}
        anchor = datetime.now(UTC) - timedelta(seconds=60)
        if existing:
            first = existing[0]
            anchor = first.timestamp - timedelta(seconds=int(first.event_metadata["seed_index"]))
        await session.commit()
        added = 0
        alerts: set[str] = set()
        for index, event in enumerate(demo_events(anchor)):
            if index not in indexes:
                _, generated = await IngestionService(session, settings).ingest(event)
                alerts.update(generated)
                added += 1
        print(f"Synthetic events added: {added}; already present: {len(indexes)}")
        print(f"Alerts touched this run: {len(alerts)}. Refresh the dashboard.")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-synthetic", required=True, action="store_true")
    parser.parse_args()
    try:
        await seed()
    finally:
        await close_engine()


if __name__ == "__main__":
    asyncio.run(main())
