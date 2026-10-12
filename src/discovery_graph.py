
from pathlib import Path

import pandas as pd
import networkx as nx

# SIGNAL ATLAS project folders
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Load existing analysis results
country_df = pd.read_csv(OUTPUTS_DIR / "country_revenue.csv")
product_df = pd.read_csv(OUTPUTS_DIR / "product_revenue.csv")
segment_df = pd.read_csv(OUTPUTS_DIR / "customer_segment_summary.csv")

graph = nx.Graph()

# Add the main discovery node
graph.add_node(
    "SIGNAL ATLAS",
    node_type="center",
    value=0
)

def add_data_nodes(data, label, node_type, value_column, top_n=10):
    """Add the highest-value records to the discovery graph."""
    if data.empty or value_column not in data.columns:
        print(f"Skipping {label}: required data is missing.")
        return

    name_column = data.columns[0]
    ranked = data.copy()
    ranked[value_column] = pd.to_numeric(
        ranked[value_column], errors="coerce"
    )
    ranked = ranked.dropna(subset=[value_column])
    ranked = ranked.nlargest(top_n, value_column)

    for _, row in ranked.iterrows():
        name = str(row[name_column])
        node_id = f"{node_type}:{name}"
        value = float(row[value_column])

        graph.add_node(
            node_id,
            label=name,
            node_type=node_type,
            value=value
        )

        graph.add_edge(
            "SIGNAL ATLAS",
            node_id,
            relationship=f"top_{label}",
            weight=value
        )

# Add countries by revenue
add_data_nodes(
    country_df, "countries_by_revenue",
    "country", "Revenue", top_n=10
)

# Add products by revenue
add_data_nodes(
    product_df, "products_by_revenue",
    "product", "Revenue", top_n=10
)

# Add customer segments
if not segment_df.empty:
    segment_name_col = next(
        (
            col for col in segment_df.columns
            if "segment" in col.lower()
        ),
        None
    )

    customer_count_col = next(
        (
            col for col in segment_df.columns
            if any(word in col.lower() for word in
                   ["customer_count", "customers", "count"])
        ),
        None
    )

    if segment_name_col and customer_count_col:
        segment_df[customer_count_col] = pd.to_numeric(
            segment_df[customer_count_col],
            errors="coerce"
        )

        for _, row in segment_df.dropna(
            subset=[customer_count_col]
        ).iterrows():
            name = str(row[segment_name_col])
            value = float(row[customer_count_col])
            node_id = f"segment:{name}"

            graph.add_node(
                node_id,
                label=name,
                node_type="customer_segment",
                value=value
            )

            graph.add_edge(
                "SIGNAL ATLAS",
                node_id,
                relationship="customer_segment",
                weight=value
            )
    else:
        print("Check customer segment column names.")

# Export graph nodes and edges
nodes = [
    {"node_id": node, **attributes}
    for node, attributes in graph.nodes(data=True)
]

edges = [
    {"source": source, "target": target, **attributes}
    for source, target, attributes in graph.edges(data=True)
]

pd.DataFrame(nodes).to_csv(
    OUTPUTS_DIR / "discovery_graph_nodes.csv",
    index=False
)

pd.DataFrame(edges).to_csv(
    OUTPUTS_DIR / "discovery_graph_edges.csv",
    index=False
)

print("\nSIGNAL ATLAS DISCOVERY GRAPH COMPLETED!")
print(f"Nodes created: {graph.number_of_nodes()}")
print(f"Connections created: {graph.number_of_edges()}")
print("Files saved:")
print(OUTPUTS_DIR / "discovery_graph_nodes.csv")
print(OUTPUTS_DIR / "discovery_graph_edges.csv")
