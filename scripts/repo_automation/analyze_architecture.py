import os
import json
import networkx as nx

def parse_repo(root_dir="."):
    """Walk the directory tree and identify structure and file types."""
    repo_structure = {}
    file_types = {}

    exclude_dirs = {'.git', '.github', '__pycache__', 'venv', 'node_modules', 'build', 'dist', '.venv'}

    for root, dirs, files in os.walk(root_dir):
        # Exclude hidden directories like .git and other noisy folders
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

        rel_path = os.path.relpath(root, root_dir)
        if rel_path == ".":
            rel_path = "root"

        repo_structure[rel_path] = {
            "dirs": dirs,
            "files": files
        }

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1

    return repo_structure, file_types

def build_knowledge_graph(repo_structure):
    """Build a graph representing directory structure."""
    G = nx.DiGraph()

    for path, contents in repo_structure.items():
        if path != "root":
            parent = os.path.dirname(path)
            if not parent:
                parent = "root"
            G.add_edge(parent, path, type="contains")

        for d in contents["dirs"]:
            child_path = os.path.join(path, d) if path != "root" else d
            G.add_node(child_path, type="dir")
            G.add_edge(path, child_path, type="contains")

        for f in contents["files"]:
            file_path = os.path.join(path, f) if path != "root" else f
            G.add_node(file_path, type="file")
            G.add_edge(path, file_path, type="contains")

    return G

def analyze():
    repo_structure, file_types = parse_repo()
    G = build_knowledge_graph(repo_structure)

    data = {
        "repo_structure": repo_structure,
        "file_types": file_types,
        "graph_nodes": list(G.nodes(data=True)),
        "graph_edges": list(G.edges(data=True))
    }

    with open("repo_graph.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    analyze()
