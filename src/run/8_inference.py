import json
import os
import networkx as nx

# 기존 그래프 불러오기: 여기서는 knowledge_graph_mini.json 동일 구조라 가정
# 실질적으로는 knowledge_graph.py에서 결과 그래프를 pickle 등으로 저장했다가 불러올 수도 있음.
JSON_PATH = "../../data/processed/knowledge_graph_mini.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 간단하게 같은 로직으로 그래프 로드 (knowledge_graph.py 로직 일부 재사용)
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

for idx, item in enumerate(data):
    incident_id = f"Incident_{idx+1}"
    graph.add_node(incident_id, type="Incident")
    cfr_nodes = add_cfr_hierarchy(graph, item["cfr"], incident_id)
    if cfr_nodes:
        cfr_leaf_node = f"{incident_id}_CFR_Level_{len(cfr_nodes)}"
    else:
        cfr_leaf_node = f"{incident_id}_CFR_Root"
        graph.add_node(cfr_leaf_node, label="No CFR Info", type="CFR")

    graph.add_edge(incident_id, cfr_leaf_node, relation="classified_as")

    for attr_key, values in item["attributes"].items():
        attr_node_id = f"{incident_id}_{attr_key}"
        graph.add_node(attr_node_id, type=attr_key)
        graph.add_edge(incident_id, attr_node_id, relation="has_attribute")

        for v_idx, val in enumerate(values):
            val_node_id = f"{incident_id}_{attr_key}_{v_idx}"
            graph.add_node(val_node_id, label=val, type="AttributeValue")
            graph.add_edge(attr_node_id, val_node_id, relation="describes")

            if attr_key == "Clause":
                import re
                match = re.search(r"(10 CFR [0-9.\(\)a-zA-Z/]+)", val)
                if match:
                    clause_str = match.group(1).strip()
                    clause_node = f"{incident_id}_{clause_str.replace(' ', '_')}"
                    graph.add_node(clause_node, label=clause_str, type="CFR_Clause")
                    graph.add_edge(incident_id, clause_node, relation="conforms_to")
                    graph.add_edge(cfr_leaf_node, clause_node, relation="specifies")


#####################
# 새로운 Incident 처리 (예시)
#####################
# 새로운 Incident 텍스트
new_incident_text = """
On July 12, 2024, the reactor protection system at Plant X automatically actuated due to a sudden drop in reactor coolant flow.
Operators took corrective actions and restored normal conditions. This seems like an RPS actuation event.
"""

# 간단한 키워드 기반 CFR 매핑 예시:
# 만약 'reactor protection system' 'automatic actuation' 키워드가 등장하면
# 10 CFR 50.73(a)(2)(iv)(A)와 관련된 CFR Clause 노드를 검색해 추천한다.

keywords = ["reactor protection system", "automatic actuation"]
matched_clauses = []

for node in graph.nodes(data=True):
    if node[1].get("type") == "CFR_Clause":
        # Clause 노드 label 확인
        label = graph.nodes[node[0]].get("label", "")
        # RPS 및 automatic actuation 관련된지 간단 검색
        # 여기서는 단순히 label 혹은 CFR 인덱스 기반으로 판단
        # 실제론 TF-IDF, embedding 등을 사용할 수 있음.
        # 10 CFR 50.73(a)(2)(iv)(A)와 연관된 incident는 RPS 자동 작동과 관련되므로
        # 키워드 매칭 기반으로 찾는 예
        if "50.73(a)(2)(iv)(A)" in label:
            # 해당 clause는 RPS 자동 작동 규정과 관련
            # 만약 new_incident_text에 자동 작동 및 RPS 키워드가 있다면 매칭
            if all(k in new_incident_text.lower() for k in keywords):
                matched_clauses.append(label)

print("New Incident Text:")
print(new_incident_text)
print("Possible CFR Clauses that might apply:", matched_clauses)
