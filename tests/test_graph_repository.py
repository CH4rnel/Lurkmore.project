# inb4: just_for_lulz

import pytest
from datetime import datetime, timezone
from src.infrastructure.database import create_pool, run_migrations
from src.graph.repository import GraphRepository


@pytest.fixture
async def db_pool():
    """Creates a test database pool and runs migrations."""
    pool = await create_pool("postgresql://lurkmore:lurkmore_pass@localhost:5433/lurkmore_db")
    await run_migrations(pool)
    yield pool
    await pool.close()


@pytest.fixture
def repository(db_pool):
    """Creates a GraphRepository instance."""
    return GraphRepository(db_pool)


@pytest.mark.asyncio
async def test_upsert_edge_insert(repository):
    """Test inserting a new edge."""
    async with repository.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (id, username, display_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            111, "user1", "User One"
        )
        await conn.execute(
            "INSERT INTO users (id, username, display_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            222, "user2", "User Two"
        )
    
    ts = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_edge(111, 222, "reply", 1.5, ts)
    
    async with repository.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM edges WHERE src_user_id = $1 AND dst_user_id = $2 AND edge_type = $3",
            111, 222, "reply"
        )
        assert row is not None
        assert row["weight"] == 1.5
        assert row["last_ts"] == ts


@pytest.mark.asyncio
async def test_upsert_edge_update(repository):
    """Test updating an existing edge weight."""
    async with repository.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (id, username, display_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            333, "user3", "User Three"
        )
        await conn.execute(
            "INSERT INTO users (id, username, display_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            444, "user4", "User Four"
        )
    
    ts1 = datetime(2026, 9, 22, 10, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_edge(333, 444, "reply", 1.0, ts1)
    
    ts2 = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_edge(333, 444, "reply", 2.5, ts2)
    
    async with repository.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM edges WHERE src_user_id = $1 AND dst_user_id = $2 AND edge_type = $3",
            333, 444, "reply"
        )
        assert row["weight"] == 2.5
        assert row["last_ts"] == ts2


@pytest.mark.asyncio
async def test_load_graph_from_db(repository):
    """Test loading graph from database as NetworkX graph."""
    # Clean edges table to ensure test isolation
    async with repository.pool.acquire() as conn:
        await conn.execute("DELETE FROM edges")
    
    # Ensure users exist
    async with repository.pool.acquire() as conn:
        for uid, uname in [(501, "u1"), (502, "u2"), (503, "u3")]:
            await conn.execute(
                "INSERT INTO users (id, username, display_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                uid, uname, uname.upper()
            )
    
    ts = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
    await repository.upsert_edge(501, 502, "reply", 2.0, ts)
    await repository.upsert_edge(502, 503, "reply", 3.0, ts)
    await repository.upsert_edge(501, 503, "reply", 1.5, ts)
    
    graph = await repository.load_graph()
    
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3
    assert graph[501][502]["weight"] == 2.0
    assert graph[502][503]["weight"] == 3.0
    assert graph[501][503]["weight"] == 1.5