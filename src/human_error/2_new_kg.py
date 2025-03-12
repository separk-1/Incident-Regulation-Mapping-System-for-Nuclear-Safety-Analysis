from py2neo import Graph, Node, Relationship
import json

# 새 데이터베이스 연결
uri = "bolt://localhost:7687"
username = "neo4j"
password = "tkfkd7274"
database_name = "humanerror"  # 사용할 데이터베이스 이름
graph = Graph(uri, auth=(username, password), name=database_name)  # 데이터베이스 이름 명시

# JSON 데이터 로드
input_file = "kg_hr.json"  # JSON 파일 이름
with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# 데이터 삽입
for record in data:
    filename = record["filename"]
    attributes = record["attributes"]
    metadata = record["metadata"]

    # Incident 노드 생성
    incident_node = Node(
        "Incident",
        filename=filename,
        title=metadata["title"],
        event_date=metadata["event_date"],
        facility=metadata["facility"]["name"],
        unit=metadata["facility"]["unit"]
    )
    graph.merge(incident_node, "Incident", "filename")

    # Task → Cause → Event → Influence → Corrective Actions 연결
    for task in attributes.get("Task", []):
        # Task 노드 생성 (공유)
        task_node = Node("Task", description=task)
        graph.merge(task_node, "Task", "description")
        # Incident → Task 관계 생성
        graph.create(Relationship(incident_node, "HAS_TASK", task_node))

        for cause in attributes.get("Cause", []):
            # Cause 노드 생성 (공유)
            cause_node = Node("Cause", description=cause)
            graph.merge(cause_node, "Cause", "description")
            # Task → Cause 관계 생성
            graph.create(Relationship(task_node, "LEADS_TO", cause_node))
            graph.create(Relationship(incident_node, "HAS_CAUSE", cause_node))

            for event in attributes.get("Event", []):
                # Event 노드 생성 (공유)
                event_node = Node("Event", description=event)
                graph.merge(event_node, "Event", "description")
                # Cause → Event 관계 생성
                graph.create(Relationship(cause_node, "TRIGGERS", event_node))
                graph.create(Relationship(incident_node, "HAS_EVENT", event_node))

                for influence in attributes.get("Influence", []):
                    # Influence 노드 생성 (공유)
                    influence_node = Node("Influence", description=influence)
                    graph.merge(influence_node, "Influence", "description")
                    # Event → Influence 관계 생성
                    graph.create(Relationship(event_node, "IMPACTS", influence_node))
                    graph.create(Relationship(incident_node, "HAS_INFLUENCE", influence_node))

                    for action in attributes.get("Corrective Actions", []):
                        # CorrectiveAction 노드 생성 (공유)
                        action_node = Node("CorrectiveAction", description=action)
                        graph.merge(action_node, "CorrectiveAction", "description")
                        # Influence → CorrectiveAction 관계 생성
                        graph.create(Relationship(influence_node, "ADDRESSED_BY", action_node))
                        graph.create(Relationship(incident_node, "HAS_CORRECTIVE_ACTION", action_node))

print("Knowledge graph created successfully.")
