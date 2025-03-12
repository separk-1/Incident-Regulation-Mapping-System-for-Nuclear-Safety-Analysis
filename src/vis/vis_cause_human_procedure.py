from neo4j import GraphDatabase
import pandas as pd
from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt

# 데이터베이스 연결 설정
uri = "bolt://localhost:7687"  # Neo4j Bolt 프로토콜 주소
username = "neo4j"             # 사용자 이름
password = "tkfkd7274"         # 비밀번호

# Neo4j 드라이버 초기화
driver = GraphDatabase.driver(uri, auth=(username, password))

# 연결 테스트
def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful' AS message")
        for record in result:
            print(record["message"])

test_connection()

# CSV 파일을 불러와서 데이터프레임 생성
file_path = './cause_distribution_filter.csv'
df = pd.read_csv(file_path)

# CSV 파일에서 Human 관련 CauseDescription 리스트 생성
df_human_list = df[df["Type"] == "Human"]["CauseDescription"].tolist()
df_procedure_list = df[df["Type"] == "Procedure"]["CauseDescription"].tolist()
print(df_procedure_list)
'''
# Neo4j 연결 설정
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Cypher 쿼리
query = """
MATCH (n:Cause)-[r]-(m)
WHERE n.description IN [
    'Human Error', 'Operational Error', 'Procedure Noncompliance', 'Improper Utilization',
    'Misinterpretation', 'Procedure Misapplication', 'Incorrect Parts', 'Miscommunication',
    'Procedural Noncompliance', 'Poor Workmanship', 'Inadequate Screening', 'Improper Maintenance',
    'Personnel Error', 'Incorrect Data Entry', 'Procedure Violation', 'Wiring Error',
    'Procedure Misreading', 'Procedure Oversight', 'Incorrect Settings', 'Procedure Negligence'
]
RETURN n.description AS node, m.description AS related_node
"""

# 쿼리 실행
results = graph.run(query)

# NetworkX 그래프 생성
G = nx.Graph()
for record in results:
    G.add_edge(record["node"], record["related_node"])

# 네트워크 시각화
plt.figure(figsize=(12, 8))
nx.draw(G, with_labels=True, node_color="lightblue", font_size=10, font_weight="bold")
plt.show()
'''