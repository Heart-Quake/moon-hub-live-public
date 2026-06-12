#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path


STATUS_OK = "OK"
STATUS_DESIGN_DRIFT = "Design drift"
STATUS_FUNCTION_DRIFT = "Function drift"
STATUS_BUILD_UNKNOWN = "Build unknown"


def run_command(command: list[str] | str, cwd: Path, timeout: int = 120) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            shell=isinstance(command, str),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return 124, f"Timeout after {timeout}s\n{error.stdout or ''}"
    return completed.returncode, completed.stdout.strip()


def git_head(repo: Path) -> str:
    code, output = run_command(["git", "rev-parse", "--short", "HEAD"], repo)
    return output if code == 0 else "unknown"


def git_dirty(repo: Path) -> str:
    code, output = run_command(["git", "status", "--short"], repo)
    if code != 0:
        return "unknown"
    return "yes" if output else "no"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def read_python_text(repo: Path) -> str:
    ignored_parts = {".git", ".venv", "venv", "__pycache__"}
    chunks = []
    if not repo.exists():
        return ""
    for path in repo.rglob("*.py"):
        if ignored_parts.intersection(path.parts):
            continue
        chunks.append(read_text(path))
    return "\n".join(chunks)


def scan_tool(tool: dict, manifest: dict, run_tests: bool) -> dict:
    workspace_root = Path(manifest["workspace_root"])
    repo = workspace_root / tool["local_path"]
    entrypoint = repo / tool["entrypoint"]
    theme_file = repo / manifest["design_requirements"]["theme_helper"]
    logo_file = repo / manifest["design_requirements"]["logo_asset"]
    config_file = repo / ".streamlit" / "config.toml"

    files_to_scan = [entrypoint, theme_file, config_file]
    searchable_text = "\n".join(read_text(path) for path in files_to_scan)
    entrypoint_text = read_text(entrypoint)
    python_text = read_python_text(repo)
    hero_present = "<section class=\"tool-hero\">" in entrypoint_text or (
        "render_app_hero()" in entrypoint_text and "<section class=\"tool-hero\">" in python_text
    )

    checks: dict[str, bool | str | list[str]] = {
        "repo_exists": repo.exists(),
        "entrypoint_exists": entrypoint.exists(),
        "theme_helper_exists": theme_file.exists(),
        "logo_asset_exists": logo_file.exists(),
        "theme_helper_loaded": "apply_automation_seo_theme()" in read_text(entrypoint),
        "hero_present": hero_present,
        "build_marker_present": "data-app-build" in searchable_text,
        "forbidden_patterns": [],
        "git_head": git_head(repo) if repo.exists() else "missing",
        "git_dirty": git_dirty(repo) if repo.exists() else "unknown",
    }

    forbidden_hits = []
    for pattern in manifest["design_requirements"]["forbidden_patterns"]:
        if pattern in searchable_text:
            forbidden_hits.append(pattern)
    checks["forbidden_patterns"] = forbidden_hits

    compile_targets = [repo / item for item in tool.get("compile_targets", [])]
    existing_compile_targets = [str(path.relative_to(repo)) for path in compile_targets if path.exists()]
    missing_compile_targets = [str(path.relative_to(repo)) for path in compile_targets if not path.exists()]
    if existing_compile_targets:
        code, output = run_command(["python3", "-m", "py_compile", *existing_compile_targets], repo)
        checks["compile_status"] = "ok" if code == 0 else "failed"
        checks["compile_output"] = output[-1200:]
    else:
        checks["compile_status"] = "missing"
        checks["compile_output"] = "No compile targets found."
    checks["missing_compile_targets"] = missing_compile_targets

    tests_dir = repo / "tests"
    if run_tests and tests_dir.exists():
        code, output = run_command(tool["test_command"], repo, timeout=240)
        checks["test_status"] = "ok" if code == 0 else "failed"
        checks["test_output"] = output[-1200:]
    elif tests_dir.exists():
        checks["test_status"] = "skipped"
        checks["test_output"] = "Use --run-tests to execute tests."
    else:
        checks["test_status"] = "none"
        checks["test_output"] = "No tests directory detected."

    design_ok = all(
        [
            checks["repo_exists"],
            checks["entrypoint_exists"],
            checks["theme_helper_exists"],
            checks["logo_asset_exists"],
            checks["theme_helper_loaded"],
            checks["hero_present"] if tool.get("requires_hero", True) else True,
            checks["build_marker_present"],
            not checks["forbidden_patterns"],
        ]
    )
    build_ok = checks["compile_status"] == "ok" and checks["test_status"] in {"ok", "skipped", "none"}

    if design_ok and build_ok:
        status = STATUS_OK
    elif not design_ok:
        status = STATUS_DESIGN_DRIFT
    elif checks["compile_status"] != "ok" or checks["test_status"] == "failed":
        status = STATUS_FUNCTION_DRIFT
    else:
        status = STATUS_BUILD_UNKNOWN

    return {
        "name": tool["name"],
        "slug": tool["slug"],
        "live_url": tool["live_url"],
        "repository_url": tool["repository_url"],
        "local_path": str(repo),
        "entrypoint": tool["entrypoint"],
        "status": status,
        "checks": checks,
    }


def write_markdown_report(results: list[dict], output_path: Path) -> None:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Audit outils live Automation SEO",
        "",
        f"Date : {now}",
        "",
        "| Outil | Statut | Commit local | Dirty | Compile | Tests | Live |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for result in results:
        checks = result["checks"]
        lines.append(
            "| {name} | {status} | `{head}` | {dirty} | {compile} | {tests} | {live} |".format(
                name=result["name"],
                status=result["status"],
                head=checks["git_head"],
                dirty=checks["git_dirty"],
                compile=checks["compile_status"],
                tests=checks["test_status"],
                live=result["live_url"],
            )
        )

    lines.extend(["", "## Détails", ""])
    for result in results:
        checks = result["checks"]
        lines.extend(
            [
                f"### {result['name']}",
                "",
                f"- Repo local : `{result['local_path']}`",
                f"- Entrypoint : `{result['entrypoint']}`",
                f"- Statut : **{result['status']}**",
                f"- Forbidden patterns : {', '.join(checks['forbidden_patterns']) if checks['forbidden_patterns'] else 'aucun'}",
                f"- Theme helper : {'oui' if checks['theme_helper_loaded'] else 'non'}",
                f"- Logo asset : {'oui' if checks['logo_asset_exists'] else 'non'}",
                f"- Hero : {'oui' if checks['hero_present'] else 'non'}",
                f"- Compile : {checks['compile_status']}",
                f"- Tests : {checks['test_status']}",
                f"- Build marker : {'oui' if checks['build_marker_present'] else 'non'}",
                "",
            ]
        )
        if checks.get("missing_compile_targets"):
            lines.append(f"- Compile targets manquants : {', '.join(checks['missing_compile_targets'])}")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local des outils Streamlit live Automation SEO.")
    parser.add_argument("--manifest", default="tools_audit_manifest.json")
    parser.add_argument("--output", default="")
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = [scan_tool(tool, manifest, args.run_tests) for tool in manifest["tools"]]

    output_path = Path(args.output) if args.output else Path("reports") / f"tools-audit-{dt.date.today().isoformat()}.md"
    write_markdown_report(results, output_path)
    print(f"Report written: {output_path}")
    for result in results:
        print(f"{result['status']}: {result['name']}")

    return 0 if all(result["status"] == STATUS_OK for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
