from pyvis.network import Network
import json

# JSON 파일 경로
KG_PATH = "../../data/processed/ler_knowledge_graph_with_clause.json"

# JSON 파일 읽기
with open(KG_PATH, "r", encoding="utf-8") as f:
    knowledge_graph = json.load(f)

# PyVis 네트워크 생성
net = Network(height="750px", width="100%", notebook=True, directed=True)

# 노드 및 엣지 추가
for data in knowledge_graph:
    # 사건 노드 추가
    incident_node = data["filename"]
    facility = data["metadata"].get("facility", "Unknown")
    event_date = data["metadata"].get("event_date", "Unknown")
    net.add_node(
        incident_node, 
        label=incident_node, 
        color="lightblue", 
        title=f"Facility: {facility}<br>Date: {event_date}"
    )

    # 속성 노드 추가 및 엣지 연결
    prev_node = None  # 이전 노드를 저장
    for attr_key in ["Event", "Cause", "Influence", "Corrective Actions"]:  # 순서대로 추가
        if attr_key in data["attributes"]:
            attr_values = data["attributes"][attr_key]
            if isinstance(attr_values, list):
                attr_value = "; ".join(attr_values)  # 리스트를 문자열로 결합
            else:
                attr_value = attr_values
            attr_node = f"{attr_key}: {attr_value}"
            attr_title = attr_value if isinstance(attr_value, str) else "No details"
            net.add_node(attr_node, label=attr_key, color="lightgreen", title=attr_title)
            net.add_edge(incident_node if prev_node is None else prev_node, attr_node)  # 이전 노드와 연결
            prev_node = attr_node  # 현재 노드를 이전 노드로 설정

    # 메타데이터 노드 추가 및 엣지 연결
    for meta_key, meta_value in data["metadata"].items():
        meta_value = str(meta_value) if not isinstance(meta_value, str) else meta_value  # 문자열로 변환
        meta_node = f"{meta_key}: {meta_value}"
        net.add_node(meta_node, label=meta_key, color="orange", title=meta_value)
        net.add_edge(incident_node, meta_node)

# 대화형 그래프 저장
output_html = "knowledge_graph_with_relationships.html"
net.show_buttons(filter_=['physics'])  # 물리 엔진 조정 버튼 추가
net.show(output_html)
print(f"Graph saved as {output_html}")
