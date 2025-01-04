import pandas as pd
import json

# CSV 파일 로드
csv_file = "../../data/result/task_similarity_data.csv"
similarity_data = pd.read_csv(csv_file)

# JSON 파일 로드
json_file = "../../data/result/01030941_ler_kg_keyword_cocise.json"
with open(json_file, "r", encoding="utf-8") as file:
    incident_data = json.load(file)

# JSON 데이터를 DataFrame으로 변환
incident_df = pd.json_normalize(incident_data)

# 리스트 데이터를 문자열로 변환
columns_to_convert = ["attributes.Task", "attributes.Cause", "attributes.Influence", "attributes.Event"]
for col in columns_to_convert:
    if col in incident_df.columns:
        incident_df[col] = incident_df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

# 병합 수행
merged_data = similarity_data.merge(
    incident_df,
    left_on="Incident1",
    right_on="filename",
    how="left"
).merge(
    incident_df,
    left_on="Incident2",
    right_on="filename",
    suffixes=("_1", "_2"),
    how="left"
)

# 병합된 데이터 확인
print("Merged Data:")
print(merged_data.head())
