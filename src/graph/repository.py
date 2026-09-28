# inb4: just_for_lulz

import asyncpg
import networkx as nx
from datetime import datetime


class GraphRepository:
    """Repository for persisting relationship graph edges."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def upsert_edge(
        self,
        src_user_id: int,
        dst_user_id: int,
        edge_type: str,
        weight: float,
        last_ts: datetime
    ) -> None:
        """Inserts or updates an edge in the relationship graph."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO edges (src_user_id, dst_user_id, edge_type, weight, last_ts)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (src_user_id, dst_user_id, edge_type) DO UPDATE
                SET weight = EXCLUDED.weight,
                    last_ts = EXCLUDED.last_ts
                """,
                src_user_id, dst_user_id, edge_type, weight, last_ts
            )
    
    async def load_graph(self) -> nx.Graph:
        """
        Loads all edges from the database as an undirected NetworkX graph.
        
        Returns:
            NetworkX Graph with nodes (user IDs) and weighted edges
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT src_user_id, dst_user_id, weight FROM edges"
            )
        
        graph = nx.Graph()
        for row in rows:
            src = row["src_user_id"]
            dst = row["dst_user_id"]
            weight = row["weight"]
            
            # Add nodes if not present
            graph.add_node(src)
            graph.add_node(dst)
            
            # For undirected graph, aggregate weights if edge already exists
            if graph.has_edge(src, dst):
                graph[src][dst]["weight"] += weight
            else:
                graph.add_edge(src, dst, weight=weight)
        
        return graph