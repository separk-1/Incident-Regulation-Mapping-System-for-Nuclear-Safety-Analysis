import csv
from py2neo import Graph

# Neo4j 연결 설정
uri = "bolt://localhost:7687"
username = "neo4j"
password = "tkfkd7274"

# Neo4j 데이터베이스 연결
graph = Graph(uri, auth=(username, password))
'''
# Cypher 쿼리
query = """
MATCH (i:Incident)-[:HAS_CAUSE]->(c:Cause)
WHERE c.description IN [
    'Human Error', 'Operational Error', 'Procedure Noncompliance', 'Improper Utilization',
    'Misinterpretation', 'Procedure Misapplication', 'Incorrect Parts', 'Miscommunication',
    'Procedural Noncompliance', 'Poor Workmanship', 'Inadequate Screening', 'Improper Maintenance',
    'Personnel Error', 'Incorrect Data Entry', 'Procedure Violation', 'Wiring Error',
    'Procedure Misreading', 'Procedure Oversight', 'Incorrect Settings', 'Procedure Negligence'
]
RETURN i.filename AS filename, c.description AS cause
"""

# 결과 실행 및 CSV 저장
output_file = "hr_list.csv"
try:
    results = graph.run(query)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Cause"])  # CSV 헤더 작성
        for record in results:
            writer.writerow([record["filename"], record["cause"]])

    print(f"Data exported successfully to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")
'''

# Cypher 쿼리
query = """
MATCH (i:Incident)-[:HAS_CAUSE]->(c:Cause)
WHERE c.description IN [
    'Inadequate Procedure', 'Procedure Error', 'Procedure Deficiency', 'Inadequate Procedures',
    'Procedure Inadequacy', 'Inadequate Guidance', 'Inadequate Procedure Guidance', 'Inadequate Work Processes'
]

RETURN i.filename AS filename, c.description AS cause
"""

# 결과 실행 및 CSV 저장
output_file = "procedure_list.csv"
try:
    results = graph.run(query)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Cause"])  # CSV 헤더 작성
        for record in results:
            writer.writerow([record["filename"], record["cause"]])

    print(f"Data exported successfully to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")