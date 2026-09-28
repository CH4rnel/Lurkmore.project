# inb4: just_for_lulz

import pytest
import networkx as nx
from src.graph.community import CommunityDetector


@pytest.fixture
def detector():
    return CommunityDetector(resolution=1.0)


def test_detect_communities_two_cliques(detector):
    """Test detection of two clearly separated communities."""
    # Build graph with two cliques connected by a weak edge
    G = nx.Graph()
    
    # Clique 1: users 1, 2, 3 (strong connections)
    G.add_edge(1, 2, weight=5.0)
    G.add_edge(2, 3, weight=5.0)
    G.add_edge(1, 3, weight=5.0)
    
    # Clique 2: users 4, 5, 6 (strong connections)
    G.add_edge(4, 5, weight=5.0)
    G.add_edge(5, 6, weight=5.0)
    G.add_edge(4, 6, weight=5.0)
    
    # Weak bridge between cliques
    G.add_edge(3, 4, weight=0.1)
    
    communities = detector.detect(G)
    
    # Should find exactly 2 communities
    assert len(communities) == 2
    
    # Each community should contain exactly 3 users
    assert len(communities[0]) == 3
    assert len(communities[1]) == 3
    
    # Users 1, 2, 3 should be in the same community
    clique1 = next(c for c in communities if 1 in c)
    assert 2 in clique1 and 3 in clique1
    
    # Users 4, 5, 6 should be in the same community
    clique2 = next(c for c in communities if 4 in c)
    assert 5 in clique2 and 6 in clique2
    
    # The two cliques should be in different communities
    assert clique1 != clique2


def test_detect_communities_empty_graph(detector):
    """Test that empty graph returns empty list."""
    G = nx.Graph()
    communities = detector.detect(G)
    assert communities == []


def test_detect_communities_single_node(detector):
    """Test that single node forms its own community."""
    G = nx.Graph()
    G.add_node(1)
    communities = detector.detect(G)
    assert len(communities) == 1
    assert 1 in communities[0]


def test_detect_communities_no_edges(detector):
    """Test that isolated nodes each form their own community."""
    G = nx.Graph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    communities = detector.detect(G)
    # Each isolated node should be its own community
    assert len(communities) == 3


def test_detect_communities_fully_connected(detector):
    """Test that fully connected graph forms single community."""
    G = nx.complete_graph(5)
    # Add weights
    for u, v in G.edges():
        G[u][v]['weight'] = 1.0
    
    communities = detector.detect(G)
    # Should be 1 community with all 5 nodes
    assert len(communities) == 1
    assert len(communities[0]) == 5