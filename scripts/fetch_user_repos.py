import urllib.request
import json
import sys

def list_repos():
    url = "https://api.github.com/users/enzonagashima/repos?per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "TestGap-Miner"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode("utf-8")
            repos = json.loads(data)
            print(f"Total repositorios encontrados: {len(repos)}")
            for r in repos:
                name = r.get("name")
                lang = r.get("language")
                desc = r.get("description")
                fork = r.get("fork")
                clone_url = r.get("clone_url")
                print(f"REPO: {name} | Lang: {lang} | Fork: {fork} | URL: {clone_url} | Desc: {desc}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    list_repos()
