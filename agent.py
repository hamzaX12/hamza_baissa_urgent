import os
import logging
import asyncio
import ssl
import json
import random
import networkx as nx
from slixmpp import ClientXMPP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CityModel:
    def __init__(self):
        # --- LOAD REAL MAP ---
        if os.path.exists("real_city.graphml"):
            self.graph = nx.read_graphml("real_city.graphml")
            # Ensure node labels are integers (GraphML loads them as strings sometimes)
            self.graph = nx.convert_node_labels_to_integers(self.graph)
            logging.info(f"🗺️  Loaded Real Map with {len(self.graph.nodes)} intersections.")
        else:
            logging.error("❌ Map file 'real_city.graphml' not found! Using fallback grid.")
            self.graph = nx.grid_2d_graph(10, 10)
            self.graph = nx.convert_node_labels_to_integers(self.graph)

    def get_distance(self, start, end):
        try:
            return nx.shortest_path_length(self.graph, source=start, target=end)
        except:
            return float('inf')

    def get_path(self, start, end):
        try:
            return nx.shortest_path(self.graph, source=start, target=end)
        except:
            return []

class SmartCityAgent(ClientXMPP):
    def __init__(self, jid, password, agent_name, role, current_node):
        super().__init__(jid, password)
        self.agent_name = agent_name
        self.role = role
        self.current_node = int(current_node)
        self.city = CityModel()
        self.received_bids = [] 
        self.light_state = "RED" 

        # SSL Fixes
        self.ssl_verify = False
        self.auto_start_tls = False 
        if hasattr(ssl, 'SSLContext'):
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199')
        self.register_plugin('xep_0077') 
        self['xep_0077'].force_registration = True

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message_received)
        self.add_event_handler("register", self.register_account)

    async def register_account(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            await resp.send()
            logging.info(f"[{self.agent_name}] Account registered.")
        except: pass

    def start(self, event):
        self.send_presence()
        self.get_roster()
        logging.info(f"[{self.agent_name}] Online at Node {self.current_node} ({self.role})")

        if self.role == "Ambulance":
            delay = random.randint(1, 3) # Fast start
            self.loop.call_later(delay, self.initiate_search)

    def initiate_search(self):
        logging.info(f"[{self.agent_name}] 🚨 EMERGENCY! Broadcasting to ALL hospitals...")
        targets = ["hospital_a@localhost", "hospital_b@localhost", "hospital_c@localhost"]
        cfp_payload = {"type": "CFP", "node": self.current_node}
        for t in targets:
            self.send_message(mto=t, mbody=json.dumps(cfp_payload), mtype='chat')

        self.loop.call_later(5, self.make_decision)

    def make_decision(self):
        if not self.received_bids:
            logging.warning(f"[{self.agent_name}] No hospitals replied!")
            return

        best_hospital = None
        shortest_dist = float('inf')
        best_path = []

        for bid in self.received_bids:
            h_node = bid['node']
            sender = bid['sender']
            dist = self.city.get_distance(self.current_node, h_node)
            path = self.city.get_path(self.current_node, h_node)
            
            if dist < shortest_dist:
                shortest_dist = dist
                best_hospital = sender
                best_path = path

        if best_hospital:
            logging.info(f"[{self.agent_name}] ✅ DESTINATION SET: {best_hospital}")
            
            self.send_message(mto=best_hospital, mbody=json.dumps({"type": "ACCEPT"}), mtype='chat')
            self.save_trip_data(best_path, best_hospital)

    def save_trip_data(self, path, best_hospital_jid):
        active_lights = path[1:-1] if len(path) > 2 else []
        hospital_nodes = [b['node'] for b in self.received_bids]
        winner_node = next(item['node'] for item in self.received_bids if item['sender'] == best_hospital_jid)
        
        trip_data = {
            "agent_name": self.agent_name,
            "start_node": self.current_node,
            "end_node": winner_node,
            "path": path,
            "traffic_lights": active_lights,
            "all_hospitals": hospital_nodes
        }
        
        filename = f"/app/output/trip_{self.agent_name}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(trip_data, f, indent=2)
            logging.info(f"[{self.agent_name}] 💾 TRIP DATA SAVED: {filename}")
        except Exception as e:
            logging.error(f"Failed to save trip data: {e}")

    def message_received(self, msg):
        if msg['type'] in ('chat', 'normal'):
            try:
                sender = msg['from'].bare
                body = json.loads(msg['body'])
                msg_type = body.get("type")

                if self.role == "Hospital" and msg_type == "CFP":
                    proposal = {"type": "PROPOSE", "node": self.current_node, "sender": str(self.boundjid.bare)}
                    self.send_message(mto=sender, mbody=json.dumps(proposal), mtype='chat')
                elif self.role == "Ambulance" and msg_type == "PROPOSE":
                    body['sender'] = sender
                    self.received_bids.append(body)
            except: pass

if __name__ == '__main__':
    jid = os.getenv('AGENT_JID')
    password = os.getenv('AGENT_PASSWORD')
    server = os.getenv('XMPP_SERVER', 'ejabberd')
    agent_name = os.getenv('AGENT_NAME')
    
    # LOAD MAP TO FIND MAX NODE ID
    if os.path.exists("real_city.graphml"):
        G = nx.read_graphml("real_city.graphml")
        max_node = len(G.nodes) - 1
    else:
        max_node = 99

    random_node = str(random.randint(0, max_node))

    if "Traffic" in agent_name:
        role = "TrafficLight"
        current_node = random_node # Simplify: Traffic lights are everywhere
    elif "Hospital" in agent_name:
        role = "Hospital"
        current_node = random_node
    else:
        role = "Ambulance"
        current_node = random_node

    logging.info(f"Starting {agent_name} ({role}) at Real-Map Node {current_node}")

    agent = SmartCityAgent(jid, password, agent_name, role, current_node)
    agent.register_plugin('xep_0077') 
    agent['xep_0077'].force_registration = True
    
    agent.connect((server, 5222))
    agent.process(forever=True)