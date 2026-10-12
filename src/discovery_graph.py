
from pathlib import Path

import pandas as pd
import networkx as nx

# SIGNAL ATLAS - DISCOVERY GRAPH

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

print("\nSIGNAL ATLAS - Discovery Graph")
print("-" * 45)

# Locate analysis files
country_file = OUTPUT_DIR / "country_revenue.csv"
product_file = OUTPUT_DIR / "product_revenue.csv"
customer_file = OUTPUT_DIR / "customer_segment_summary.csv"

for file in [country_file, product_file, customer_file]:
    if not file.exists():
        raise FileNotFoundError(
            f"Required file not found: {file}\n"
            "Please run the corresponding analysis scripts first."
        )

# Load the existing analysis outputs
countries = pd.read_csv(country_file)
products = pd.read_csv(product_file)
customers = pd.read_csv(customer_file)

if countries.empty or products.empty or customers.empty:
    raise ValueError("One or more analysis files contain no data.")

# Create graph
graph = nx.Graph()

# Add country nodes
for _, row in countries.head(10).iterrows():
    country = str(row.iloc[0])
    graph.add_node(
        f"Country: {country}",
        node_type="Country",
    )

# Add product nodes
for _, row in products.head(10).iterrows():
    product = str(row.iloc[0])
    graph.add_node(
        f"Product: {product}",
        node_type="Product",
    )

# Add customer segment nodes
for _, row in customers.iterrows():
    segment = str(row["Customer_Segment"])
    graph.add_node(
        f"Customer Segment: {segment}",
        node_type="Customer Segment",
    )

# Add a central node connecting the findings
central_node = "SIGNAL ATLAS: Business Insights"
graph.add_node(central_node, node_type="Central Insight")

for node in list(graph.nodes):
    if node != central_node:
        graph.add_edge(
            central_node,
            node,
            relationship="Included in business analysis",
        )

# Export graph nodes
nodes = [
    {
        "Node": node,
        "Node_Type": attrs.get("node_type", "Unknown"),
    }
    for node, attrs in graph.nodes(data=True)
]

pd.DataFrame(nodes).to_csv(
    OUTPUT_DIR / "discovery_graph_nodes.csv",
    index=False,
)

# Export graph connections
edges = [
    {
        "Source": source,
        "Target": target,
        "Relationship": attrs.get("relationship", ""),
    }
    for source, target, attrs in graph.edges(data=True)
]

pd.DataFrame(edges).to_csv(
    OUTPUT_DIR / "discovery_graph_edges.csv",
    index=False,
)

print(f"Nodes created: {graph.number_of_nodes()}")
print(f"Connections created: {graph.number_of_edges()}")
print("Saved discovery_graph_nodes.csv")
print("Saved discovery_graph_edges.csv")
print("\nDISCOVERY GRAPH COMPLETED SUCCESSFULLY!")
