from sentence_transformers import SentenceTransformer, util
from neo4j import GraphDatabase
import json
import pandas as pd
from tqdm import tqdm

# Load the model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Neo4j connection settings
uri = "bolt://localhost:7687"  # Neo4j URL
username = "neo4j"  # 사용자 이름
password = "tkfkd7274"  # 비밀번호
driver = GraphDatabase.driver(uri, auth=(username, password))

# Load JSON data
with open("../../data/processed/01030941_ler_kg_keyword_cocise.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Load CFR data
cfr_file = "../../data/processed/3_cfr_concise.csv"
cfr_data = pd.read_csv(cfr_file)

# Convert CFR data to dictionary
cfr_dict = cfr_data.set_index("CFR")[["content_3", "content_4"]].to_dict(orient="index")

def delete_all_nodes_and_relationships(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("All existing nodes and relationships have been deleted.")

# Function to insert CFR nodes into Neo4j
def insert_cfr_nodes(tx, cfr, content_3, content_4):
    tx.run(
        """
        MERGE (c:CFR {cfr: $cfr})
        SET c.upper = $upper, c.lower = $lower
        """,
        cfr=cfr, upper=content_3, lower=content_4
    )

# Function to insert nodes and relationships into Neo4j
def insert_nodes_and_relationships(tx, event_data):
    # Insert Incident node
    tx.run("""
    MERGE (i:Incident {filename: $filename})
    SET i.title = $title, i.date = $date
    """, filename=event_data["filename"], title=event_data["metadata"]["title"], date=event_data["metadata"]["event_date"])

    # Insert and relate Task
    for task in event_data["attributes"]["Task"]:
        tx.run("""
        MERGE (t:Task {description: $task})
        MERGE (i:Incident {filename: $filename})
        MERGE (i)-[:RELATED_TO_TASK]->(t)
        """, task=task, filename=event_data["filename"])

    # Insert and relate other attributes
    attributes = ["Event", "Cause", "Influence", "Corrective Actions"]
    for attribute in attributes:
        for item in event_data["attributes"].get(attribute, []):
            tx.run(f"""
            MERGE ({attribute.lower()[:2]}:{attribute.replace(" ", "")} {{description: $item}})
            MERGE (i:Incident {{filename: $filename}})
            MERGE (i)-[:HAS_{attribute.upper().replace(" ", "_")}]->({attribute.lower()[:2]})
            """, item=item, filename=event_data["filename"])

    # Insert and relate Facility
    tx.run("""
    MERGE (f:Facility {name: $facility_name, unit: $facility_unit})
    MERGE (i:Incident {filename: $filename})
    MERGE (i)-[:OCCURRED_AT]->(f)
    """, facility_name=event_data["metadata"]["facility"]["name"], 
          facility_unit=event_data["metadata"]["facility"]["unit"], 
          filename=event_data["filename"])

    # Insert and relate Clause
    clauses = event_data["metadata"]["clause"].split(", ")
    for clause in clauses:
        if clause in cfr_dict:
            upper = cfr_dict[clause]["content_3"]
            lower = cfr_dict[clause]["content_4"]
            tx.run("""
            MERGE (cl:CFR {cfr: $clause})
            SET cl.upper = $upper, cl.lower = $lower
            MERGE (i:Incident {filename: $filename})
            MERGE (i)-[:REGULATED_BY]->(cl)
            """, clause=clause, upper=upper, lower=lower, filename=event_data["filename"])

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
        return util.pytorch_cos_sim(emb1, emb2).item()
    return 0.0  # Return 0 if text is missing

# Function to insert relationships into Neo4j
def insert_task_based_relationship(tx, filename1, filename2, task1, task2, task_similarity, cause_similarity, event_similarity, influence_similarity):
    """
    Insert a relationship between two incidents based on task similarity and add other similarities as properties.
    """
    tx.run(
        """
        MATCH (e1:Incident {filename: $filename1}), (e2:Incident {filename: $filename2}),
              (t1:Task {description: $task1}), (t2:Task {description: $task2})
        MERGE (e1)-[r:SIMILAR_TASK]->(e2)
        SET r.task_similarity = $task_similarity,
            r.cause_similarity = $cause_similarity,
            r.event_similarity = $event_similarity,
            r.influence_similarity = $influence_similarity,
            r.task1 = $task1,
            r.task2 = $task2
        """,
        filename1=filename1,
        filename2=filename2,
        task1=task1,
        task2=task2,
        task_similarity=task_similarity,
        cause_similarity=cause_similarity,
        event_similarity=event_similarity,
        influence_similarity=influence_similarity,
    )

# Step 1: Clear existing data from Neo4j
delete_all_nodes_and_relationships(driver)

# Step 2: Insert CFR nodes
with driver.session() as session:
    for cfr, values in cfr_dict.items():
        session.write_transaction(insert_cfr_nodes, cfr, values["content_3"], values["content_4"])

# Step 3: Insert all nodes and relationships
with driver.session() as session:
    for event in data:
        session.write_transaction(insert_nodes_and_relationships, event)

# Step 4: Calculate task-based similarities and create relationships
with driver.session() as session:
    for i in tqdm(range(len(data)), desc="Processing incidents", total=len(data)):
        event1 = data[i]
        for task1 in event1["attributes"]["Task"]:
            for j in range(i + 1, len(data)):  # Avoid duplicate comparisons
                event2 = data[j]
                for task2 in event2["attributes"]["Task"]:
                    # Calculate similarity for tasks
                    task_similarity = calculate_similarity("Task", event1, event2)

                    # Calculate other similarities for context
                    cause_similarity = calculate_similarity("Cause", event1, event2)
                    event_similarity = calculate_similarity("Event", event1, event2)
                    influence_similarity = calculate_similarity("Influence", event1, event2)

                    if task_similarity >= 0.8:  # Only connect if task similarity is above threshold
                        print(f"Connecting {event1['filename']} and {event2['filename']} based on Task '{task1}' and '{task2}' with similarity {task_similarity:.2f}")
                        session.write_transaction(
                            insert_task_based_relationship,
                            event1["filename"],
                            event2["filename"],
                            task1,
                            task2,
                            task_similarity,
                            cause_similarity,
                            event_similarity,
                            influence_similarity,
                        )

print("Task-based relationships and similarity data have been added to Neo4j.")
driver.close()
