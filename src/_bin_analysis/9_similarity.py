from neo4j import GraphDatabase
import pandas as pd
import os

# Neo4j 연결 설정
uri = "bolt://localhost:7687"  # Neo4j URL
username = "neo4j"  # 사용자 이름
password = "tkfkd7274"  # 비밀번호

# 데이터베이스 연결 설정
driver = GraphDatabase.driver(uri, auth=(username, password))

def fetch_data(query):
    """
    네오4제이에서 쿼리를 실행하고 결과를 Pandas DataFrame으로 반환.
    """
    with driver.session() as session:
        result = session.run(query)
        return pd.DataFrame([record.data() for record in result])

# Task 간 유사성 관계 가져오는 쿼리
task_similarity_query = """
MATCH (e1:Incident)-[r:SIMILAR_TASK]->(e2:Incident)
RETURN e1.filename AS Incident1, e2.filename AS Incident2,
       r.task_similarity AS TaskSimilarity,
       r.cause_similarity AS CauseSimilarity,
       r.event_similarity AS EventSimilarity,
       r.influence_similarity AS InfluenceSimilarity
ORDER BY TaskSimilarity DESC
"""

# 연결 테스트
def test_connection():
    try:
        with driver.session() as session:
            session.run("RETURN 1")
        print("Successfully connected to Neo4j!")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")

test_connection()

# 데이터 가져오기
similarity_data = fetch_data(task_similarity_query)

if similarity_data.empty:
    print("No data found. The query returned an empty result.")
else:
    print(f"Data fetched successfully. Number of rows: {len(similarity_data)}")
    print(similarity_data.head())

# 데이터 저장
output_directory = "../../data/analysis"
os.makedirs(output_directory, exist_ok=True)
output_file = os.path.join(output_directory, "task_similarity_data.csv")

try:
    similarity_data.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Data saved to {output_file}")
except Exception as e:
    print(f"Failed to save data: {e}")

# 데이터베이스 연결 닫기
driver.close()
