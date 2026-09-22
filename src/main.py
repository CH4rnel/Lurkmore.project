# inb4: just_for_lulz

import asyncio
import logging
from dotenv import load_dotenv
import os

from src.infrastructure.database import create_pool, run_migrations
from src.ingestion.telegram_client import create_telegram_client
from src.ingestion.repository import MessageRepository
from src.ingestion.service import IngestionService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for chat ingestion."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    database_url = os.getenv("DATABASE_URL")
    chat_id = int(os.getenv("INGEST_CHAT_ID", "-1001234567890"))  # TODO: configure
    limit = int(os.getenv("INGEST_LIMIT", "100"))
    
    logger.info("Starting Lurkmore Ingestion Service")
    
    # Initialize database
    logger.info("Connecting to PostgreSQL...")
    pool = await create_pool(database_url)
    await run_migrations(pool)
    logger.info("Database initialized")
    
    # Initialize Telegram client
    logger.info("Connecting to Telegram...")
    telegram_client = create_telegram_client()
    await telegram_client.connect()
    logger.info("Telegram client connected")
    
    # Initialize repository and service
    repository = MessageRepository(pool)
    service = IngestionService(telegram_client, repository)
    
    try:
        # Run ingestion
        ingested = await service.ingest_chat(chat_id, limit)
        logger.info(f"Ingestion complete: {ingested} messages processed")
        
    finally:
        # Cleanup
        await telegram_client.disconnect()
        await pool.close()
        logger.info("Connections closed")


if __name__ == "__main__":
    asyncio.run(main())