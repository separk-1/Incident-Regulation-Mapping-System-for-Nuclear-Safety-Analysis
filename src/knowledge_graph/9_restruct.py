from neo4j import GraphDatabase

def restructure_graph_relationships(graph):
    """
    Restructure relationships in the Neo4j graph to establish logical flow:
    Task -> Cause -> Event -> Influence -> Corrective Action
    """
    queries = [
        # Task → Cause
        """
        MATCH (i:Incident)-[:RELATED_TO_TASK]->(t:Task), (i)-[:HAS_CAUSE]->(c:Cause)
        MERGE (t)-[:CAUSES]->(c)
        """,
        # Cause → Event
        """
        MATCH (i:Incident)-[:HAS_CAUSE]->(c:Cause), (i)-[:HAS_EVENT]->(e:Event)
        MERGE (c)-[:TRIGGERS]->(e)
        """,
        # Event → Influence
        """
        MATCH (i:Incident)-[:HAS_EVENT]->(e:Event), (i)-[:HAS_INFLUENCE]->(inf:Influence)
        MERGE (e)-[:IMPACTS]->(inf)
        """,
        # Influence → Corrective Action
        """
        MATCH (i:Incident)-[:HAS_INFLUENCE]->(inf:Influence), (i)-[:HAS_CORRECTIVE_ACTIONS]->(ca:CorrectiveAction)
        MERGE (inf)-[:ADDRESSED_BY]->(ca)
        """
    ]
    
    for query in queries:
        graph.run(query)

if __name__ == "__main__":
    # Neo4j connection settings
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "tkfkd7274"
    
    # Connect to Neo4j
    graph = GraphDatabase.driver(uri, auth=(username, password))
    
    # Restructure relationships
    with graph.session() as session:
        restructure_graph_relationships(session)
    
    print("Graph relationships have been restructured.")
