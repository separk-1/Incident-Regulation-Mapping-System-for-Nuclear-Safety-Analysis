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

# K-means 클러스터링 실행
optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
data["Cluster"] = kmeans.fit_predict(X)

# 클러스터링 결과 시각화 (2D)
plt.figure(figsize=(10, 6))
scatter = plt.scatter(X[:, 0], X[:, 1], c=data["Cluster"], cmap="viridis", s=50)
plt.title(f"K-means Clustering with K={optimal_k}")
plt.xlabel("TaskSimilarity")
plt.ylabel("CauseSimilarity")
plt.colorbar(scatter, label="Cluster")

# PNG로 저장
png_output = "../../data/analysis/kmeans_clustering.png"
plt.savefig(png_output, dpi=300, bbox_inches="tight")
plt.show()

# 클러스터링 결과 출력
print("Clustered Data:")
print(data[["Incident1", "Incident2", "Cluster"]])

# 클러스터링 결과 DataFrame 저장
csv_output = "../../data/analysis/kmeans_clustering_results.csv"
data.to_csv(csv_output, index=False, encoding="utf-8-sig")
print(f"Clustered Data saved to {csv_output}")

# 클러스터 중심점 출력
print("Cluster Centers:")
print(kmeans.cluster_centers_)

# 클러스터별 평균 값 계산 및 저장
cluster_summary = data.groupby("Cluster")[features].mean()
print("Cluster Summary:")
print(cluster_summary)

# 클러스터 요약 저장
summary_output = "../../data/analysis/kmeans_cluster_summary.csv"
cluster_summary.to_csv(summary_output, index=True, encoding="utf-8-sig")
print(f"Cluster Summary saved to {summary_output}")
