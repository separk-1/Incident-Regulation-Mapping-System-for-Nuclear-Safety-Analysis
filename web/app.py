from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer, util
from neo4j import GraphDatabase
import openai
import os
from dotenv import load_dotenv

# Flask 애플리케이션 설정
app = Flask(__name__)

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
        f"Incident: {r['incident']}, Task: {r['task']}, Cause: {r['cause']}, Date: {r['date']}"
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
            {"role": "system", "content": "You are a helpful assistant for analyzing incident patterns based on graph data."},
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

# Flask 라우트 설정
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "No question provided."}), 400

        # 질문 처리
        answer = answer_question(question)
        return jsonify({"answer": answer, "references": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=5001)
