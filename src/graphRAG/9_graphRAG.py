from sentence_transformers import SentenceTransformer, util
from neo4j import GraphDatabase
import openai
import os
from dotenv import load_dotenv

# Neo4j 연결 설정
uri = "bolt://localhost:7687"
username = "neo4j"
password = "tkfkd7274"
driver = GraphDatabase.driver(uri, auth=(username, password))

# 모델 로드
model = SentenceTransformer("all-MiniLM-L6-v2")

# OpenAI API 키 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 질문을 파싱하고 키워드 추출
def extract_keywords(question, graph_keywords):
    """
    Extract relevant keywords from the question.
    """
    question_embedding = model.encode(question, convert_to_tensor=True)
    keyword_embeddings = model.encode(graph_keywords, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(question_embedding, keyword_embeddings).squeeze()
    top_keywords = [graph_keywords[i] for i in similarities.argsort(descending=True)[:3]]
    return top_keywords

# Neo4j 탐색 쿼리 실행
def query_graph(tx, keywords):
    """
    Query Neo4j graph based on extracted keywords.
    """
    query = """
    MATCH (t:Task)-[:RELATED_TO_TASK]-(i:Incident)-[:HAS_CAUSE]->(c:Cause)
    WHERE t.description IN $keywords
    RETURN i.title AS incident, t.description AS task, c.description AS cause, i.date AS date
    LIMIT 10
    """
    result = tx.run(query, keywords=keywords)
    return [record.data() for record in result]

# 질문에 대한 답변 생성
def generate_answer(question, graph_results):
    """
    Generate a natural language answer using OpenAI ChatGPT.
    """
    context = "\n".join(
    f"""Incident: {r['incident']}
        Task: {r['task']}
        Cause: {r['cause']}
        Event: {r.get('event', 'N/A')}
        Influence: {r.get('influence', 'N/A')}
        Corrective Actions: {r.get('corrective_actions', 'N/A')}
        Facility: {r.get('facility', {}).get('name', 'Unknown')} - Unit: {r.get('facility', {}).get('unit', 'Unknown')}
        Clause: {r.get('clause', 'N/A')}
        Date: {r['date']}
    """
    for r in graph_results
)

    prompt = f"""
    User Question: {question}
    Relevant Graph Data:
    {context}

    Based on the above data, provide a concise and helpful response to the user.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content":
            "You are a technical assistant specializing in incident pattern analysis for nuclear reactors. Your job is to analyze graph data and provide a structured list of incidents, including their names, dates, causes, impacts, and corrective actions, with accurate references."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0
    )
    return response["choices"][0]["message"]["content"].strip()


# 메인 함수: 질문 -> 답변
def answer_question(question):
    # 키워드 추출
    graph_keywords = ["Reactor Inspection", "System Testing", "Maintenance", "Reactor Startup"]  # 지식 그래프의 Task 키워드
    keywords = extract_keywords(question, graph_keywords)

    # Neo4j 탐색
    with driver.session() as session:
        graph_results = session.read_transaction(query_graph, keywords)

    # LLM 응답 생성
    if graph_results:
        return generate_answer(question, graph_results)
    else:
        return "No relevant data found in the graph."

# 예제 질문 실행
question = "What are the most likely incidents to occur during system testing?"
answer = answer_question(question)
print(answer)
