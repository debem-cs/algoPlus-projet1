"""Bundle the existing helpers and V2 into a self-contained algorithm.py."""

import ast
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


def main():
    project = Path(__file__).resolve().parent
    base = (project / "solution/algorithm.py").read_text(encoding="utf-8")
    entry = ast.parse(base).body[-1]
    if not isinstance(entry, ast.FunctionDef) or entry.name != "dominant":
        raise ValueError("The base module must end with dominant(g)")
    base = "".join(base.splitlines(keepends=True)[:entry.lineno - 1])

    improved = (project / "solution/improved_search.py").read_text(encoding="utf-8")
    lines = improved.splitlines(keepends=True)
    for node in ast.parse(improved).body:
        if isinstance(node, ast.ImportFrom) and node.module == "algorithm":
            lines[node.lineno - 1:node.end_lineno] = [""] * (node.end_lineno - node.lineno + 1)
    combined = base + "\n\n# Version 2: broader deterministic search.\n" + "".join(lines)
    ast.parse(combined, feature_version=(3, 7))

    output = project / "submissions/improved_search_v2.zip"
    member = zipfile.ZipInfo("algorithm.py", date_time=(1980, 1, 1, 0, 0, 0))
    member.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(output, "w") as bundle:
        bundle.writestr(member, combined.encode("utf-8"))

    previous = project / "submissions/archive_v1/best_of_all.zip"
    previous.parent.mkdir(exist_ok=True)
    if not previous.exists() and (project / "submission.zip").exists():
        shutil.copyfile(project / "submission.zip", previous)
    shutil.copyfile(output, project / "submission.zip")
    manifest = {
        "archive": output.name,
        "files": ["algorithm.py"],
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "python_syntax_target": "3.7",
        "external_imports": [],
        "root_submission_matches_v2": True,
    }
    results = project / "results/improved"
    results.mkdir(parents=True, exist_ok=True)
    (results / "submission_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
