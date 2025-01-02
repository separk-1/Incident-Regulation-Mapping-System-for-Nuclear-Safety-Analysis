def cluster_by_cfr(filename, attributes, cfr_hierarchy):
    cluster = {
        "filename": filename,
        "cfr": {
            "content_1": cfr_hierarchy.get("content_1", ""),
            "content_2": cfr_hierarchy.get("content_2", ""),
            "content_3": cfr_hierarchy.get("content_3", ""),
            "content_4": cfr_hierarchy.get("content_4", "")
        },
        "attributes": attributes
    }
    return cluster

knowledge_clusters = []

for i, row in tqdm(ler_df.iterrows(), total=len(ler_df), desc="Processing rows"):
    # Combine text from selected columns
    combined_text = " ".join(
        str(row.get(col, "")) for col in ["Abstract", "Narrative"]
    )

    extracted_attributes = extract_attributes(combined_text)

    if extracted_attributes:
        cfr_hierarchy = {
            "content_1": row.get("content_1", ""),
            "content_2": row.get("content_2", ""),
            "content_3": row.get("content_3", ""),
            "content_4": row.get("content_4", "")
        }
        cluster = cluster_by_cfr(row.get("filename", ""), extracted_attributes, cfr_hierarchy)
        knowledge_clusters.append(cluster)

print("\nKnowledge Clusters (sample):")
print(knowledge_clusters[:3])


# Save results to JSON
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_clusters, json_file, indent=4, ensure_ascii=False)
    
# Save results to JSON
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_clusters, json_file, indent=4, ensure_ascii=False)