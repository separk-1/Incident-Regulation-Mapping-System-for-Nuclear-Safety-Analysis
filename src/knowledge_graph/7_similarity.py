import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# JSON file path
KG_PATH = "../../data/processed/ler_knowledge_graph_with_clause.json"

# Load JSON file
with open(KG_PATH, "r", encoding="utf-8") as f:
    knowledge_graph = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to calculate similarity for a specific attribute
def calculate_similarity(attribute, data1, data2):
    """
    Calculate similarity between two events (data1, data2) for a specific attribute.
    """
    text1 = " ".join(data1["attributes"].get(attribute, []))
    text2 = " ".join(data2["attributes"].get(attribute, []))
    if text1 and text2:  # Calculate only if both texts are available
        emb1 = model.encode(text1, convert_to_tensor=True)
        emb2 = model.encode(text2, convert_to_tensor=True)
        return cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0))[0][0]
    return 0.0  # Return 0 if text is missing

# Function to calculate overall similarity with weights
def calculate_total_similarity(data1, data2, weights):
    """
    Calculate total similarity between two events, weighted by attributes.
    """
    similarities = {}
    total_similarity = 0.0
    for attribute, weight in weights.items():
        similarity = calculate_similarity(attribute, data1, data2)
        similarities[attribute] = similarity
        total_similarity += similarity * weight
    return total_similarity, similarities

# Attribute weights
weights = {
    "Event": 0.4,
    "Cause": 0.3,
    "Influence": 0.2,
    "Corrective Actions": 0.1,
}

# Create similarity matrix between events
num_events = len(knowledge_graph)
similarity_matrix = np.zeros((num_events, num_events))
attribute_similarities = {}  # Store similarities for each attribute

for i, data1 in enumerate(knowledge_graph):
    for j, data2 in enumerate(knowledge_graph):
        if i != j:  # Skip self-similarity
            total_similarity, similarities = calculate_total_similarity(data1, data2, weights)
            similarity_matrix[i, j] = total_similarity
            attribute_similarities[(i, j)] = similarities

# Print similarity matrix
print("Event Similarity Matrix:")
print(similarity_matrix)

# Function to find the most similar events for a specific event
def find_most_similar_event(event_index, similarity_matrix, knowledge_graph, top_n=3):
    """
    Find the top N most similar events for a specific event, including attribute-level similarities.
    """
    similarities = similarity_matrix[event_index]
    top_indices = np.argsort(similarities)[-top_n:][::-1]  # Sort top N similarities
    similar_events = []
    for i in top_indices:
        attribute_sims = attribute_similarities[(event_index, i)]
        similar_events.append({
            "filename": knowledge_graph[i]["filename"],
            "total_similarity": similarities[i],
            "attribute_similarities": attribute_sims
        })
    return similar_events

# Find similar events for a specific event
event_index = 0  # Use the first event as the reference
most_similar = find_most_similar_event(event_index, similarity_matrix, knowledge_graph)
print(f"\nThe most similar events to {knowledge_graph[event_index]['filename']}:")

# Print results with attribute-level similarities
for event in most_similar:
    print(f"Filename: {event['filename']}, Total Similarity: {event['total_similarity']:.2f}")
    for attribute, similarity in event["attribute_similarities"].items():
        print(f"  {attribute} Similarity: {similarity:.2f}")
