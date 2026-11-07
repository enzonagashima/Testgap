import os
import subprocess
from pathlib import Path

REPOS = [
    "access-counter",
    "AsyncNotify",
    "SpeakApp",
    "RecaptchaBot",
    "workshoppeniel",
    "E2E-test-suite",
    "API.nodejs"
]

CLONE_DIR = Path("data/cloned_repos/enzonagashima")
CLONE_DIR.mkdir(parents=True, exist_ok=True)

def clone_repos():
    for repo in REPOS:
        target = CLONE_DIR / repo
        if target.exists():
            print(f"[=] Ja clonado: {repo}")
            continue
        url = f"https://github.com/enzonagashima/{repo}.git"
        print(f"[*] Clonando {repo} de {url}...")
        res = subprocess.run(["git", "clone", "--depth", "1", url, str(target)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Sucesso: {repo}")
        else:
            print(f"[-] Erro ao clonar {repo}: {res.stderr}")

if __name__ == "__main__":
    clone_repos()
