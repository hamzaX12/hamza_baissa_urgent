import os
import json
import glob
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

OUTPUT_DIR = "./output"
MAP_FILE = "real_city.graphml"

def animate_all():
    print(f"🔍 Loading Real Map from {MAP_FILE}...")
    if not os.path.exists(MAP_FILE):
        print("❌ Map file missing! Run create_real_map.py first.")
        return

    # Load Real Map
    G = nx.read_graphml(MAP_FILE)
    G = nx.convert_node_labels_to_integers(G)
    
    # Extract positions (latitude/longitude)
    pos = {}
    for node, data in G.nodes(data=True):
        # GraphML usually stores 'x' (lon) and 'y' (lat)
        if 'x' in data and 'y' in data:
            pos[node] = (float(data['x']), float(data['y']))
        else:
            pos[node] = (0, 0) # Fallback

    # Load Trips
    json_files = glob.glob(os.path.join(OUTPUT_DIR, "trip_*.json"))
    trips = []
    for f in json_files:
        with open(f, 'r') as file:
            data = json.load(file)
            if data.get('path'): trips.append(data)

    if not trips:
        print("❌ No valid trips found.")
        return

    fig, ax = plt.subplots(figsize=(12, 12))
    amb_colors = ['blue', 'cyan', 'purple', 'magenta', 'orange']
    max_frames = max(len(t['path']) for t in trips) + 5

    def update(frame):
        ax.clear()
        ax.set_facecolor('#f0f0f0')

        # Draw Real Streets
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#999999', width=2, alpha=0.8)

        # Collect static elements
        all_hospitals = set()
        all_traffic_lights = set() # Master list of lights
        active_lights_at_frame = set()

        for t in trips:
            all_hospitals.update(t['all_hospitals'])
            # We assume every node in the path acts as a traffic light potential
            all_traffic_lights.update(t['traffic_lights'])
            
            path = t['path']
            idx = min(frame, len(path)-1)
            
            # Lights turned green by THIS ambulance so far
            traversed = set(path[:idx+1])
            active_lights_at_frame.update(traversed.intersection(set(t['traffic_lights'])))

        # Draw Hospitals
        for node in all_hospitals:
            if node in pos:
                x, y = pos[node]
                # Scale marker size for map coordinates (approx 0.0002 deg)
                rect = patches.Rectangle((x-0.0002, y-0.0002), 0.0004, 0.0004, color='red', zorder=5)
                ax.add_patch(rect)

        # Draw Traffic Lights (Red by default, Green if activated)
        for node in all_traffic_lights:
            if node in pos:
                x, y = pos[node]
                color = '#00ff00' if node in active_lights_at_frame else 'red'
                circle = patches.Circle((x, y), radius=0.0001, color=color, zorder=10)
                ax.add_patch(circle)

        # Draw Ambulances
        for i, trip in enumerate(trips):
            path = trip['path']
            idx = min(frame, len(path)-1)
            curr = path[idx]
            
            if curr in pos:
                x, y = pos[curr]
                color = amb_colors[i % len(amb_colors)]
                # Ambulance marker
                circle = patches.Circle((x, y), radius=0.00015, color=color, zorder=20)
                ax.add_patch(circle)

        ax.set_title(f"REAL MAP SIMULATION: Mexico City\nFrame {frame}/{max_frames}")
        ax.set_aspect('equal') # Keep map proportions correct
        ax.axis('off')

    print("🎬 Generating Real-Map Animation...")
    ani = animation.FuncAnimation(fig, update, frames=max_frames, interval=500, repeat=False)
    ani.save(os.path.join(OUTPUT_DIR, "real_city_simulation.gif"), writer='pillow')
    print("✅ Done!")

if __name__ == "__main__":
    animate_all()