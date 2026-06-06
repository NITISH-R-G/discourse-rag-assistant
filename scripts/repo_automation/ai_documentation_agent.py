import os
import json
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

def get_repo_data():
    if os.path.exists("repo_graph.json"):
        with open("repo_graph.json", "r") as f:
            return json.load(f)
    return {}

def get_diagram():
    if os.path.exists("docs/architecture/system_diagram.md"):
        with open("docs/architecture/system_diagram.md", "r") as f:
            return f.read()
    return ""

def generate_ai_summary(repo_data):
    """Uses OpenAI to generate an architectural summary based on repo data."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not found, skipping AI summary generation.")
        return "*(AI Summary skipped: No OpenAI API key provided)*"

    try:
        client = OpenAI(api_key=api_key)

        # We simplify the data sent to the AI to avoid huge token costs
        summary_data = {
            "file_types": repo_data.get("file_types", {}),
            "top_level_structure": {
                k: v for k, v in repo_data.get("repo_structure", {}).items()
                if k == "root" or not "/" in k
            }
        }

        prompt = f"""
        You are an AI repository maintainer. Analyze the following summary of a codebase's structure
        and generate a brief, professional architectural overview suitable for a README.md file.
        Focus on what the system likely does based on the file types and directory names.

        Codebase summary:
        {json.dumps(summary_data, indent=2)}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful software architecture expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating AI summary: {e}")
        return f"*(Failed to generate AI summary: {e})*"

def update_readme():
    """Regenerates the README.md using a Jinja2 template and parsed repo data."""
    repo_data = get_repo_data()
    diagram = get_diagram()

    file_types = repo_data.get("file_types", {})
    structure = repo_data.get("repo_structure", {})

    ai_summary = generate_ai_summary(repo_data)

    env = Environment(loader=FileSystemLoader("scripts/repo_automation"))
    template = env.get_template("README.template.md")

    output = template.render(
        file_types=file_types,
        structure=structure,
        diagram=diagram,
        ai_summary=ai_summary
    )

    with open("README.md", "w") as f:
        f.write(output)

    print("README.md updated successfully.")

if __name__ == "__main__":
    update_readme()
