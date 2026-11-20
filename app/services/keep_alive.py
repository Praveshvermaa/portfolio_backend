
import asyncio
import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

async def keep_alive():
    url = settings.backend_url.rstrip("/") + "/health"

    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            try:
                response = await client.get(url)
                logger.info("Keep-alive status: %s", response.status_code)
            except Exception:
                logger.exception("Keep-alive request failed")

            await asyncio.sleep(300)
