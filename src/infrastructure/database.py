# inb4: just_for_lulz

import asyncpg
from pathlib import Path


async def create_pool(database_url: str) -> asyncpg.Pool:
    """
    Creates an async connection pool to PostgreSQL.
    
    Args:
        database_url: PostgreSQL connection string (e.g., postgresql://user:pass@host:port/db)
    
    Returns:
        asyncpg.Pool: Connection pool instance
    """
    return await asyncpg.create_pool(database_url)


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
            sql = sql_file.read_text()
            await conn.execute(sql)