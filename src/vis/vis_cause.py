from neo4j import GraphDatabase
import pandas as pd

# 데이터베이스 연결 설정
uri = "bolt://localhost:7687"  # Neo4j Bolt 프로토콜 주소
username = "neo4j"            # 사용자 이름
password = "tkfkd7274"        # 비밀번호

# Neo4j 드라이버 초기화
driver = GraphDatabase.driver(uri, auth=(username, password))

# 연결 테스트
def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful' AS message")
        for record in result:
            print(record["message"])

test_connection()

# Cypher 쿼리 실행 함수
def fetch_data(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters)
        return [dict(record) for record in result]  # 각 레코드를 dict 형태로 변환

# 원인별 사건 수 가져오기 (description 사용)
query = """
MATCH (c:Cause)<-[:HAS_CAUSE]-(i:Incident)
RETURN c.description AS CauseDescription, COUNT(i) AS IncidentCount
ORDER BY IncidentCount DESC
"""
data = fetch_data(query)

# DataFrame 변환
df = pd.DataFrame(data)

# 결과 출력 및 CSV 저장
if not df.empty:
    print(df)
    # CSV 파일로 저장
    output_file = "cause_distribution.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Data has been saved to {output_file}")
else:
    print("No data found.")
