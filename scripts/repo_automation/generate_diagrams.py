import json
import os

def generate_mermaid():
    """Reads the knowledge graph and outputs a Mermaid diagram."""
    if not os.path.exists("repo_graph.json"):
        print("repo_graph.json not found.")
        return

    with open("repo_graph.json", "r") as f:
        data = json.load(f)

    mermaid_lines = ["```mermaid", "graph TD;"]

    edges = data.get("graph_edges", [])

    # Simple top level mapping to keep diagram size reasonable
    # For a real implementation, we could group by folder or service
    for edge in edges:
        source = edge[0]
        target = edge[1]

        # Clean up node names for mermaid (remove spaces/special chars)
        src_clean = source.replace(".", "_").replace("/", "_").replace("-", "_")
        tgt_clean = target.replace(".", "_").replace("/", "_").replace("-", "_")

        mermaid_lines.append(f"    {src_clean}[\"{source}\"] --> {tgt_clean}[\"{target}\"];")

    mermaid_lines.append("```")

    os.makedirs("docs/architecture", exist_ok=True)
    with open("docs/architecture/system_diagram.md", "w") as f:
        f.write("\n".join(mermaid_lines))

    print("Generated Mermaid diagram at docs/architecture/system_diagram.md")

if __name__ == "__main__":
    generate_mermaid()
