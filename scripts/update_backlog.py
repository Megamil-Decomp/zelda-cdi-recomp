#!/usr/bin/env python3
"""Render public progress; optionally read the registered GitHub issues.

No media, private reports or local Git credentials are read. GitHub mode uses
the caller's GITHUB_TOKEN/GH_TOKEN and never changes issues or project fields.
"""
import argparse
from collections import Counter
from datetime import date
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- BACKLOG:START -->"
END = "<!-- BACKLOG:END -->"
STATES = {"backlog": "Backlog", "in_progress": "Em andamento",
          "validation": "A validar", "done": "Concluído"}
AREAS = {
    "base": ("Base e fidelidade", "Foundation and fidelity"),
    "runtime": ("Recompilação e runtime", "Recompilation and runtime"),
    "compatibilidade": ("Compatibilidade dos jogos", "Game compatibility"),
    "interface": ("Interface e controles", "Interface and controls"),
    "plataformas": ("Plataformas e exportação", "Platforms and export"),
    "localizacao": ("Localização PT-BR", "PT-BR localization"),
}
LABELS = {"status:backlog": "backlog", "status:em-andamento": "in_progress",
          "status:a-validar": "validation", "status:concluido": "done"}


def validate(document):
    if document.get("schema_version") != 1:
        raise ValueError("Unsupported backlog schema")
    repository = document.get("repository", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid GitHub repository")
    if not re.fullmatch(r"https://github\.com/users/[A-Za-z0-9-]+/projects/\d+(?:/views/\d+)?",
                        document.get("project_url") or ""):
        raise ValueError("Invalid public project URL")
    date.fromisoformat(document["snapshot_date"])
    ids, numbers = set(), set()
    if not isinstance(document.get("items"), list):
        raise ValueError("Items must be a list")
    for item in document["items"]:
        if not re.fullmatch(r"ZCDI-\d{3}", item["id"]) or item["id"] in ids:
            raise ValueError("Invalid or duplicate item identity")
        ids.add(item["id"])
        number = item.get("issue_number")
        if type(number) is not int or number <= 0 or number in numbers:
            raise ValueError("Every item requires a unique positive issue number")
        numbers.add(number)
        if item["status"] not in STATES or item["area"] not in AREAS:
            raise ValueError("Unknown status or area")
        if item["priority"] not in ("P0", "P1", "P2", "P3"):
            raise ValueError("Unknown priority")
        for field in ("title", "acceptance"):
            if not isinstance(item[field], str) or not item[field].strip() or any(c in item[field] for c in "\n\r<>|"):
                raise ValueError("Invalid public item text")
        path = Path(item["evidence"])
        if not path.parts or path.is_absolute() or ".." in path.parts or path.parts[0] not in ("docs", "app", "scripts", "tests"):
            raise ValueError("Evidence must reference a public source path")
    return document


def stats(items):
    counts = Counter(item["status"] for item in items)
    total = len(items)
    return total, counts, round(100 * counts["done"] / total) if total else 0


def issue_status(issue):
    if issue.get("state") == "closed":
        # A cancelled task is not an accepted delivery.
        return "backlog" if issue.get("state_reason") == "not_planned" else "done"
    states = {LABELS[label["name"]] for label in issue.get("labels", [])
              if label.get("name") in LABELS}
    if len(states) > 1:
        raise ValueError("Conflicting status labels on a registered issue")
    state = next(iter(states), "backlog")
    return "validation" if state == "done" else state


def sync_issues(document, issues):
    registered = {i["number"]: i for i in issues if "pull_request" not in i}
    updates = []
    for item in document["items"]:
        if item["issue_number"] not in registered:
            raise ValueError("Registered issue missing; refusing partial refresh")
        state = issue_status(registered[item["issue_number"]])
        if item["status"] != state:
            updates.append((item, state))
    for item, state in updates:
        item["status"] = state
    changes = len(updates)
    if changes:
        document["snapshot_date"] = date.today().isoformat()
    return changes


def fetch_issues(repository, token):
    issues = []
    for page in range(1, 101):
        url = f"https://api.github.com/repos/{repository}/issues?state=all&per_page=100&page={page}"
        request = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(request, timeout=30) as response:
            rows = json.load(response)
        if not isinstance(rows, list):
            raise ValueError("Unexpected GitHub response")
        issues.extend(rows)
        if len(rows) < 100:
            return issues
    raise ValueError("Issue pagination limit exceeded")


def area_table(document, english=False):
    lines = (["| Area | Done / planned | Deliveries |", "| --- | ---: | ---: |"] if english else
             ["| Área | Concluídas / cadastradas | Entregas |", "| --- | ---: | ---: |"])
    for area, names in AREAS.items():
        total, counts, percent = stats([i for i in document["items"] if i["area"] == area])
        lines.append(f"| {names[1 if english else 0]} | {counts['done']} / {total} | {percent}% |")
    return "\n".join(lines)


def summary(document, english=False, docs_page=False):
    total, counts, percent = stats(document["items"])
    url = document["project_url"]
    backlog = "BACKLOG.md" if docs_page else "docs/BACKLOG.md"
    if english:
        text = (f"[Open the Kanban board]({url}) · [Backlog and acceptance criteria]({backlog})\n\n"
                f"**{counts['done']} / {total} registered deliveries completed ({percent}%)** · updated {document['snapshot_date']}.\n\n"
                f"Done: **{counts['done']}** · In progress: **{counts['in_progress']}** · Awaiting validation: **{counts['validation']}** · Backlog: **{counts['backlog']}**.\n\n"
                "This counts scoped deliveries equally; it is not a percentage of complete campaigns, effort, fidelity or native-code coverage. Scope changes can lower the percentage.\n\n")
    else:
        text = (f"[Abrir quadro Kanban]({url}) · [Backlog e critérios de aceitação]({backlog})\n\n"
                f"**{counts['done']} / {total} entregas cadastradas concluídas ({percent}%)** · atualizado em {document['snapshot_date']}.\n\n"
                f"Concluído: **{counts['done']}** · Em andamento: **{counts['in_progress']}** · A validar: **{counts['validation']}** · Backlog: **{counts['backlog']}**.\n\n"
                "A contagem dá o mesmo peso a cada entrega; não é percentual de campanha, esforço, fidelidade ou cobertura nativa. Ampliar o escopo pode reduzir o percentual.\n\n")
    return text + area_table(document, english) + "\n"


def render_backlog(document):
    url = document["project_url"]
    text = ("# Backlog e progresso\n\n"
            "<!-- Generated by scripts/update_backlog.py from docs/backlog.json. -->\n\n" + summary(document, docs_page=True) + "\n"
            "## Como interpretar\n\n"
            "Percentual = entregas concluídas ÷ entregas cadastradas × 100, arredondado ao inteiro. Nenhum avanço parcial foi estimado. Uma campanha inteira e uma ferramenta têm pesos iguais nesta contagem; por isso ela não prevê prazo ou esforço restante.\n\n"
            "Em andamento significa frente iniciada com pendências documentadas, sem promessa de execução em segundo plano. A validar significa implementação ou build pronta aguardando ensaio real. Concluído vale apenas para o escopo de cada cartão, não para todos os caminhos dos jogos.\n\n"
            "Os percentuais de instruções nativas publicados em [PROGRESS.md](PROGRESS.md) são outra métrica: dependem do percurso, incluem BIOS quando declarado e não certificam compatibilidade completa.\n\n"
            "## Quadro\n\n")
    grouped = {state: [i for i in document["items"] if i["status"] == state] for state in STATES}
    text += "| Backlog | Em andamento | A validar | Concluído |\n| --- | --- | --- | --- |\n"
    for index in range(max((len(items) for items in grouped.values()), default=0)):
        cells = []
        for items in grouped.values():
            if index >= len(items):
                cells.append("—")
            else:
                item = items[index]
                cells.append(f"[{item['id']} · {item['title']}](https://github.com/{document['repository']}/issues/{item['issue_number']})")
        text += "| " + " | ".join(cells) + " |\n"
    text += "\n## Critérios por entrega\n\n"
    for item in document["items"]:
        issue = f"https://github.com/{document['repository']}/issues/{item['issue_number']}"
        text += (f"- [{item['id']} · {item['title']}]({issue}) — **{STATES[item['status']]}**, {item['priority']}. "
                 f"{item['acceptance']} [Referência](../{item['evidence']}).\n")
    text += ("\n## Manutenção\n\n"
             "Fechar uma issue como concluída conta como entrega aceita; fechar como não planejada não conta como concluída. Para trabalho aberto, use uma única label `status:backlog`, `status:em-andamento` ou `status:a-validar`. Reabrir uma entrega concluída a devolve à validação. O resumo usa as issues, não a posição visual dos cartões.\n\n"
             "O workflow `Atualizar backlog` lê essas mudanças e atualiza os dois READMEs, esta página e o JSON, usando apenas o token efêmero do Actions. Se a branch impedir push automático, consulte o log e execute o comando local. Nenhuma credencial pessoal é adicionada.\n\n"
             "`python3 scripts/update_backlog.py` regenera a documentação a partir de `docs/backlog.json`; `--check` verifica divergências. `--sync-github` lê o estado das issues usando `GITHUB_TOKEN` ou `GH_TOKEN`. Para ampliar o escopo, cadastre a issue no JSON com critério de aceitação e referência pública. Novas issues não entram silenciosamente no denominador.\n\n"
             f"O [Project]({url}) permite mover cartões visualmente; atualize também a label ou feche/reabra a issue para refletir a mudança no resumo. Não há sincronização de campos privados do Projects pelo token de Actions. Logs, mídia, saves e pacotes completos continuam fora do GitHub.\n")
    return text


def replace_summary(text, content):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(END) < text.index(START):
        raise ValueError("README must have exactly one ordered pair of backlog markers")
    before, rest = text.split(START)
    _, after = rest.split(END)
    return before + START + "\n" + content + END + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--sync-github", action="store_true")
    args = parser.parse_args()
    if args.check and args.sync_github:
        parser.error("--check cannot refresh remote data")
    source = ROOT / "docs/backlog.json"
    document = validate(json.loads(source.read_text()))
    if args.sync_github:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token:
            parser.error("GitHub sync requires GITHUB_TOKEN or GH_TOKEN")
        sync_issues(document, fetch_issues(document["repository"], token))
        validate(document)
    outputs = {ROOT / "docs/BACKLOG.md": render_backlog(document)}
    for name, english in (("README.md", True), ("README.pt-BR.md", False)):
        path = ROOT / name
        outputs[path] = replace_summary(path.read_text(), summary(document, english))
    if args.sync_github:
        outputs[source] = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    different = [p for p, content in outputs.items() if not p.exists() or p.read_text() != content]
    if args.check and different:
        parser.exit(1, "Stale backlog: " + ", ".join(str(p.relative_to(ROOT)) for p in different) + "\n")
    if not args.check:
        for path in different:
            path.write_text(outputs[path])
    total, counts, percent = stats(document["items"])
    print(f"Backlog: {counts['done']}/{total} ({percent}%); {len(different)} files {'stale' if args.check else 'updated'}")


if __name__ == "__main__":
    main()
