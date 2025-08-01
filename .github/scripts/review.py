import os
import openai
from github import Github
import subprocess

# Configura tus claves
openai.api_key = os.environ["OPENAI_API_KEY"]
gh = Github(os.environ["GITHUB_TOKEN"])
repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

# 1) Genera diff entre base y head
diff = subprocess.run(
    ["git", "diff", f"origin/{pr.base.ref}", pr.head.ref],
    capture_output=True,
    text=True,
    check=True
).stdout

# 2) Prepara prompt para ChatGPT
prompt = f"""
Revisa este diff de código. Para cada archivo cambiado, señala:
- Errores de lógica o security bugs.
- Posibles mejoras de estilo, legibilidad y mejores prácticas.
Devuélvelo en formato de lista, agrupado por archivo.
```diff
{diff}

