"""Run yearly depreciation recalculation for all assets (book value -= depreciation_rate%)."""

import asyncio
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.core.database import async_session_factory
from app.models.asset import Asset


async def run_depreciation() -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Asset).where(
                Asset.current_book_value.isnot(None),
                Asset.depreciation_rate.isnot(None),
                Asset.status == "active",
            )
        )
        assets = result.scalars().all()
        updated = 0
        for asset in assets:
            rate = float(asset.depreciation_rate or 0) / 100
            new_value = float(asset.current_book_value or 0) * (1 - rate)
            if new_value < 0:
                new_value = 0
            await session.execute(
                update(Asset).where(Asset.id == asset.id).values(current_book_value=Decimal(str(new_value)))
            )
            updated += 1
        await session.commit()
        print(f"Updated book value for {updated} assets.")


if __name__ == "__main__":
    asyncio.run(run_depreciation())
