import os
import pickle
import openai
import networkx as nx
from flask import Flask, request, render_template_string
import webbrowser

# 환경변수에서 OPENAI_API_KEY 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")

# 피클로 저장한 그래프 로딩
GRAPH_PKL_PATH = "../../data/knowledge_graph/graph_mini.pkl"
with open(GRAPH_PKL_PATH, "rb") as f:
    graph = pickle.load(f)

# 미리 만들어둔 PyVis HTML (graph_mini.html)
KG_HTML_PATH = "../../data/knowledge_graph/graph_mini.html"


app = Flask(__name__)

# 메인 페이지 템플릿(심플한 inline template)
index_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Incident CFR & Similar Cases</title>
<style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    textarea { width: 100%; height: 150px; }
    .result { margin-top: 20px; }
    iframe { width: 100%; height: 600px; border: 1px solid #ccc; margin-top: 20px; }
</style>
</head>
<body>
<h1>Enter Incident Description</h1>
<form method="POST" action="/analyze">
    <textarea name="incident_text" placeholder="Describe the incident..."></textarea><br><br>
    <input type="submit" value="Analyze">
</form>
</body>
</html>
"""

# 결과 페이지 템플릿
result_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analysis Result</title>
<style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .result-section { margin-bottom: 20px; }
    iframe { width: 100%; height: 600px; border: 1px solid #ccc; margin-top: 20px; }
</style>
</head>
<body>
<h1>Analysis Result</h1>
<div class="result-section">
    <h2>Analysis</h2>
    <pre>{{gpt_analysis}}</pre>
</div>

<div class="result-section">
    <h2>Matched CFR</h2>
    <pre>{{matched_cfr}}</pre>
</div>

<div class="result-section">
    <h2>Similar Incidents</h2>
    <pre>{{similar_incidents}}</pre>
</div>

<h2>Knowledge Graph Visualization</h2>
<iframe src="/kg"></iframe>

</body>
</html>
"""

def gpt_extract_info(incident_text):
    messages = [
        {"role": "system", "content": "You are an expert in nuclear incident analysis and CFR mapping."},
        {"role": "user",
         "content": f"""
Given the following incident description:

\"\"\"{incident_text}\"\"\"

1. Extract key systems, events, or causes from this description.
2. Suggest which CFR clauses might be relevant based on the presence of reactor protection system actuation or other triggers.
3. Suggest if there are any similar past incidents (like if the incident involves RPS actuation or coolant flow issues).
"""}
    ]

    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response.choices[0].message["content"]

def gpt_match_cfr(incident_text, cfr_clauses_list):
    clauses_str = "\n".join(cfr_clauses_list)
    messages = [
        {"role": "system", "content": "You are a CFR classification assistant."},
        {"role": "user", "content": f"""
Incident description:
\"\"\"{incident_text}\"\"\"

We have the following CFR clauses from the graph:
{clauses_str}

Which CFR clause from the above list best matches the conditions described in the incident?
If multiple match, suggest the most relevant one.
"""}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response.choices[0].message["content"]

def gpt_find_similar_incidents(incident_text, incident_list):
    incidents_str = "\n".join(incident_list)
    messages = [
        {"role": "system", "content": "You are an incident similarity analyst."},
        {"role": "user", "content": f"""
We have a new incident:
\"\"\"{incident_text}\"\"\"

We have these past incidents:
{incidents_str}

Based on the description, which of the past incidents might be similar (e.g., mention reactor protection system, coolant flow issues, or generator testing)?
Just guess from the names if they follow a similar pattern.
"""}
    ]
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, temperature=0.5)
    return response.choices[0].message["content"]

@app.route("/", methods=["GET"])
def index():
    return index_template

@app.route("/analyze", methods=["POST"])
def analyze():
    incident_text = request.form.get("incident_text", "")

    # GPT 기반 분석
    gpt_analysis = gpt_extract_info(incident_text)

    # 그래프에서 CFR Clause와 Incidents 추출
    cfr_clauses = [n for n, d in graph.nodes(data=True) if d.get("type") == "CFR_Clause"]
    incidents = [n for n, d in graph.nodes(data=True) if d.get("type") == "Incident"]

    matched_cfr = gpt_match_cfr(incident_text, cfr_clauses) if cfr_clauses else "No CFR clauses found."
    similar_incidents = gpt_find_similar_incidents(incident_text, incidents) if incidents else "No other incidents found."

    rendered = render_template_string(
        result_template,
        gpt_analysis=gpt_analysis,
        matched_cfr=matched_cfr,
        similar_incidents=similar_incidents
    )
    return rendered

@app.route("/kg")
def kg():
    # knowledge graph html 파일을 그대로 return
    with open(KG_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

if __name__ == "__main__":
    # Flask 실행 시 자동으로 브라우저 열기 (옵션)
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)
    app.run(debug=True)
