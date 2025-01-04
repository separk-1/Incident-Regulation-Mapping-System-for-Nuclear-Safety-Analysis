import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

# CSV 파일 읽기
input_file = "../../data/analysis/task_similarity_data.csv"
data = pd.read_csv(input_file)

# 데이터 확인
print("Loaded Data:")
print(data.head())

# 클러스터링에 사용할 열 선택
features = ["TaskSimilarity", "CauseSimilarity", "EventSimilarity", "InfluenceSimilarity"]
data[features] = data[features].fillna(0)  # NaN 값 0으로 대체
X = data[features].to_numpy()

# 엘보우 방법으로 최적의 클러스터 개수 찾기
distortions = []
K = range(1, 10)
for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    distortions.append(kmeans.inertia_)

# 엘보우 방법 그래프 그리기 및 저장
plt.figure(figsize=(10, 6))
plt.plot(K, distortions, marker="o")
plt.title("Elbow Method for Optimal K")
plt.xlabel("Number of Clusters (K)")
plt.ylabel("Distortion")
plt.savefig("elbow_method_for_optimal_k.png", dpi=300, bbox_inches="tight")  # 그래프 저장
plt.show()
