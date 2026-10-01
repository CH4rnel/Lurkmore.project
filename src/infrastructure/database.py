# inb4: just_for_lulz

import asyncpg
import json
from pathlib import Path


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Initialize connection with JSON/JSONB codec."""
    await conn.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )


async def create_pool(database_url: str) -> asyncpg.Pool:
    """
    Creates an async connection pool to PostgreSQL with JSON codec.
    
    Args:
        database_url: PostgreSQL connection string
    
    Returns:
        asyncpg.Pool: Connection pool instance
    """
    return await asyncpg.create_pool(database_url, init=_init_connection)


async def run_migrations(pool: asyncpg.Pool, migrations_dir: str = "migrations") -> None:
    """
    Executes all SQL migration files in the specified directory.
    
    Args:
        pool: Database connection pool
        migrations_dir: Path to directory containing .sql migration files
    """
    migrations_path = Path(migrations_dir)
    sql_files = sorted(migrations_path.glob("*.sql"))
    
    async with pool.acquire() as conn:
        for sql_file in sql_files:
            sql = sql_file.read_text().strip()
            if sql:
                await conn.execute(sql)