from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt

def filter_and_visualize_graph(graph):
    """
    Filter the graph for Task -> Cause -> Event -> Influence -> Corrective Actions
    relationships and visualize it.
    """
    # Cypher query to filter Task -> Cause -> Event -> Influence -> Corrective Actions
    query = """
    MATCH (t:Task)-[:CAUSES]->(c:Cause)-[:TRIGGERS]->(e:Event)-[:IMPACTS]->(i:Influence)-[:ADDRESSED_BY]->(ca:CorrectiveActions)
    RETURN t.description AS task, c.description AS cause, e.description AS event, i.description AS influence, ca.description AS corrective_action
    """

    try:
        # Execute the query
        results = graph.run(query)

        # Create a directed graph using NetworkX
        G = nx.DiGraph()

        for record in results:
            task = record.get("task", "Unknown Task")
            cause = record.get("cause", "Unknown Cause")
            event = record.get("event", "Unknown Event")
            influence = record.get("influence", "Unknown Influence")
            corrective_action = record.get("corrective_action", "Unknown Corrective Action")

            # Add edges to the graph
            G.add_edge(task, cause, label="CAUSES")
            G.add_edge(cause, event, label="TRIGGERS")
            G.add_edge(event, influence, label="IMPACTS")
            G.add_edge(influence, corrective_action, label="ADDRESSED_BY")

        # Check if the graph is empty
        if G.number_of_nodes() == 0:
            print("No data found for the specified query.")
            return

                # Visualize the graph
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)  # Layout for better visualization
        nx.draw_networkx(
            G, pos, with_labels=True, node_color="lightblue", font_size=10, font_weight="bold", arrows=True
        )
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels={(u, v): d["label"] for u, v, d in G.edges(data=True)}, font_size=8
        )
        plt.title("Task → Cause → Event → Influence → Corrective Actions", fontsize=14)
        plt.show()


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Neo4j connection settings
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "tkfkd7274"

    try:
        # Connect to Neo4j
        graph = Graph(uri, auth=(username, password))

        # Filter and visualize the graph
        filter_and_visualize_graph(graph)

        print("Visualization complete.")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
