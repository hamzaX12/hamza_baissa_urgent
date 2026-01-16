import osmnx as ox
import networkx as nx

def create_map():
    print("🌍 Downloading map for 'Texas Medical Center' (World's Largest Medical City)...")
    
    # 1. Download the street network for the specific medical district
    # "Texas Medical Center" is a recognized place in OpenStreetMap
    G = ox.graph_from_place('Texas Medical Center, Houston, Texas, USA', network_type='drive')
    
    # 2. Convert to undirected graph
    G = G.to_undirected()
    
    # 3. Convert complex OSM IDs to simple integers (0, 1, 2...) for your agents
    G = nx.convert_node_labels_to_integers(G, label_attribute='osm_id')
    
    # 4. Save to file
    filename = "real_city.graphml"
    ox.save_graphml(G, filename)
    
    print(f"✅ Map saved as '{filename}'.")
    print(f"   - Nodes (Intersections): {len(G.nodes)}")
    print(f"   - Edges (Roads): {len(G.edges)}")

if __name__ == "__main__":
    create_map()