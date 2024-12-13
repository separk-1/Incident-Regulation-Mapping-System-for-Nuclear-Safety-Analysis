import json
import os
import networkx as nx
from pyvis.network import Network
import re
import pickle

# JSON 파일 경로
JSON_PATH = "../../data/processed/knowledge_graph.json"
KG_PATH = "../../data/knowledge_graph/graph.html"
GRAPH_PKL_PATH = "../../data/knowledge_graph/graph.pkl"  # 그래프 저장 경로

# 이미지에 제시된 관계 매핑 테이블
RELATION_MAP = {
    ("Event", "Cause"): "Causes",
    ("Event", "Influence"): "Results In",
    ("Event", "Corrective Actions"): "Mitigated By",
    ("Event", "Similar Events"): "Related To",
    ("Cause", "Event"): "Explains",
    ("Cause", "Influence"): "Leads To",
    ("Influence", "Corrective Actions"): "Addressed By",
    ("Influence", "Guideline"): "Guided By",
    ("Corrective Actions", "Guideline"): "Recommended By",
    ("Corrective Actions", "Event"): "Addresses",
    ("Similar Events", "Cause"): "Shares Cause",
    ("Guideline", "Clause"): "Contains",
    ("Guideline", "Event"): "Referenced By",
    ("Clause", "Corrective Actions"): "Suggests"
}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

graph = nx.DiGraph()

def add_cfr_hierarchy(graph, cfr_content, base_id):
    cfr_nodes = []
    for i in range(1, 5):
        c = cfr_content.get(f"content_{i}")
        if c and c.strip():
            cfr_nodes.append(c.strip())

    for i in range(len(cfr_nodes)):
        node_name = f"{base_id}_CFR_Level_{i+1}"
        graph.add_node(node_name, label=cfr_nodes[i], type="CFR")
        if i > 0:
            prev_node = f"{base_id}_CFR_Level_{i}"
            graph.add_edge(prev_node, node_name, relation="has_subcategory")

    return cfr_nodes

# incident별 attribute value 노드 저장용
incident_attr_values = {}  # {incident_id: {attr_key: [value_node_ids]}}

for idx, item in enumerate(data):
    # Incident 노드 생성 (각 사건)
    incident_id = f"Incident_{idx+1}"
    graph.add_node(incident_id, type="Incident", label=f"Incident {idx+1}")

    # CFR 계층 추가
    cfr_nodes = add_cfr_hierarchy(graph, item["cfr"], incident_id)
    if cfr_nodes:
        cfr_leaf_node = f"{incident_id}_CFR_Level_{len(cfr_nodes)}"
    else:
        cfr_leaf_node = f"{incident_id}_CFR_Root"
        graph.add_node(cfr_leaf_node, label="No CFR Info", type="CFR")

    graph.add_edge(incident_id, cfr_leaf_node, relation="classified_as")

    attribute_values = {}
    for attr_key, values in item["attributes"].items():
        attr_node_id = f"{incident_id}_{attr_key.replace(' ', '_')}"
        graph.add_node(attr_node_id, type=attr_key, label=attr_key)
        graph.add_edge(incident_id, attr_node_id, relation="has_attribute")

        value_node_ids = []
        for v_idx, val in enumerate(values):
            val_node_id = f"{incident_id}_{attr_key}_{v_idx}"
            graph.add_node(val_node_id, label=val, type="AttributeValue")
            graph.add_edge(attr_node_id, val_node_id, relation="describes")
            value_node_ids.append(val_node_id)

            # Clause에서 CFR Clause 노드 추출
            if attr_key == "Clause":
                match = re.search(r"(10 CFR [0-9.\(\)a-zA-Z/]+)", val)
                if match:
                    clause_str = match.group(1).strip()
                    clause_node = f"{incident_id}_{clause_str.replace(' ', '_')}"
                    if not graph.has_node(clause_node):
                        graph.add_node(clause_node, label=clause_str, type="CFR_Clause")
                        graph.add_edge(incident_id, clause_node, relation="conforms_to")
                        graph.add_edge(cfr_leaf_node, clause_node, relation="specifies")

        attribute_values[attr_key] = value_node_ids
    incident_attr_values[incident_id] = attribute_values

# 속성 타입들 간에 테이블에 정의된 관계를 생성
for incident_id, attrs in incident_attr_values.items():
    attr_keys = list(attrs.keys())
    for source_attr in attr_keys:
        for target_attr in attr_keys:
            if source_attr == target_attr:
                continue
            key = (source_attr, target_attr)
            if key in RELATION_MAP:
                relation_label = RELATION_MAP[key]
                # source_attr values -> target_attr values 모든 쌍 연결
                for s_node in attrs[source_attr]:
                    for t_node in attrs[target_attr]:
                        # 엣지 추가 (Value 노드 간 관계)
                        graph.add_edge(s_node, t_node, relation=relation_label)

# 그래프를 pickle로 저장
with open(GRAPH_PKL_PATH, "wb") as pf:
    pickle.dump(graph, pf)

print(f"Graph saved to {GRAPH_PKL_PATH}")

# PyVis 네트워크 생성
net = Network(height="1000px", width="100%", directed=True)
net.from_nx(graph)

# 노드 hover title 설정
for node in net.nodes:
    n_id = node["id"]
    n_type = graph.nodes[n_id].get("type", "Unknown")
    label = graph.nodes[n_id].get("label", n_id)
    node["title"] = f"{label} (Type: {n_type})"

# 색상 설정 (예시)
for node in net.nodes:
    n_type = graph.nodes[node["id"]].get("type", "")
    if n_type == "CFR":
        node["color"] = "#f0a500"
    elif n_type == "Incident":
        node["color"] = "#7dafff"
    elif n_type == "CFR_Clause":
        node["color"] = "#ffa07a"
    elif n_type == "AttributeValue":
        node["color"] = "#b0b0b0"
    else:
        node["color"] = "#cccccc"

net.set_options("""
var options = {
  "layout": {
    "hierarchical": {
      "enabled": false
    }
  },
  "interaction": {
    "hover": true,
    "zoomView": true
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -30000
    }
  }
}
""")

net.write_html(KG_PATH, notebook=False)
print(f"Knowledge graph visual saved to {KG_PATH}")
