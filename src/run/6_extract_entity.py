import openai
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import os
import re
import json

# 환경 변수에서 API 키 불러오기
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 파일 경로 설정
LER_DF_PATH = "../../data/processed/ler_df_filtered.csv"  # 첫 번째 CSV 경로
LER_CFR_PATH = "../../data/processed/ler_cfr.csv"  # 두 번째 CSV 경로
CFR_PATH = "../../data/processed/cfr.csv"  # CFR 설명 CSV 경로
OUTPUT_JSON = "../../data/processed/knowledge_graph.json"  # JSON 저장 경로

# 데이터 읽기
ler_data = pd.read_csv(LER_DF_PATH)
ler_cfr_data = pd.read_csv(LER_CFR_PATH)
cfr_data = pd.read_csv(CFR_PATH)

# 두 파일의 File Name 열에서 일치하는 항목만 필터링
common_files = set(ler_data["File Name"]).intersection(set(ler_cfr_data["filename"]))
filtered_data = ler_data[ler_data["File Name"].isin(common_files)]

# filename 기준으로 ler_cfr_data와 병합
filtered_data = pd.merge(filtered_data, ler_cfr_data, left_on="File Name", right_on="filename", how="inner")

# CFR 기준으로 cfr_data와 병합
filtered_data = pd.merge(filtered_data, cfr_data, on="CFR", how="left")

# 데이터 병합 결과 디버깅 출력
print("\nFiltered data after merging (sample):")
print(filtered_data.head())

# 각 행의 텍스트에서 필요한 요소 추출 함수
def extract_attributes(text):
    try:
        messages = [
            {"role": "system", "content": "You are an expert in incident analysis and attribute extraction."},
            {"role": "user", "content": f"""
            Analyze the following text and extract the following attributes:

            - Event: Key events that occurred.
            - Cause: The cause or reasons for the event.
            - Influence: The influence or impact of the event.
            - Corrective Actions: Actions taken to address the issue.
            - Similar Events: Similar events reported in the past.
            - Guideline: Procedures or guidelines referenced.
            - Clause: Specific clauses or rules cited.

            Text: \"{text}\"

            Output the results in JSON format with keys matching the attributes listed above.
            """},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=1200,
        )
        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"GPT API 에러 발생: {e}")
        return None

# 지식 그래프 데이터 파싱 및 클러스터링 함수
def cluster_by_cfr(attributes, cfr_hierarchy):
    cluster = {
        "cfr": {
            "content_1": cfr_hierarchy.get("content_1", ""),
            "content_2": cfr_hierarchy.get("content_2", ""),
            "content_3": cfr_hierarchy.get("content_3", ""),
            "content_4": cfr_hierarchy.get("content_4", "")
        },
        "attributes": attributes
    }
    return cluster

# 지식 그래프 생성
knowledge_clusters = []

for i, row in tqdm(filtered_data.iterrows(), total=len(filtered_data), desc="Processing rows"):
    # 텍스트 결합
    combined_text = " ".join(
        str(row.get(col, "")) for col in ["Abstract", "Narrative"]
    )

    # 속성 추출
    extracted_attributes = extract_attributes(combined_text)

    if extracted_attributes:
        # CFR 기반 클러스터 생성
        cfr_hierarchy = {
            "content_1": row.get("content_1", ""),
            "content_2": row.get("content_2", ""),
            "content_3": row.get("content_3", ""),
            "content_4": row.get("content_4", "")
        }
        cluster = cluster_by_cfr(extracted_attributes, cfr_hierarchy)
        knowledge_clusters.append(cluster)

# 중간 결과 출력
print("\nKnowledge Clusters (sample):")
print(knowledge_clusters[:3])

# 결과 저장
with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_clusters, json_file, indent=4, ensure_ascii=False)

print(f"\n지식 클러스터 데이터가 {OUTPUT_JSON}에 저장되었습니다.")
