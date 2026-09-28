# inb4: just_for_lulz

import networkx as nx
from networkx.algorithms import community as nx_community


class CommunityDetector:
    """
    Detects communities in a relationship graph using Louvain method.
    
    Implements modularity maximization from §5.6:
    Q = (1 / 2m) * Σ_ij [ A_ij - (k_i k_j)/(2m) ] * δ(c_i, c_j)
    """
    
    def __init__(self, resolution: float = 1.0):
        """
        Args:
            resolution: Resolution parameter for Louvain method.
                       Higher values → more communities.
        """
        self.resolution = resolution
    
    def detect(self, graph: nx.Graph) -> list[set[int]]:
        """
        Detects communities in the graph.
        
        Args:
            graph: NetworkX graph with weighted edges
        
        Returns:
            List of communities, where each community is a set of node IDs
        """
        if graph.number_of_nodes() == 0:
            return []
        
        # Louvain method from NetworkX
        communities = nx_community.louvain_communities(
            graph,
            weight="weight",
            resolution=self.resolution,
            seed=42  # For reproducibility
        )
        
        return [set(c) for c in communities]