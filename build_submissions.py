"""Package one Codabench ZIP per strategy and the combined submission."""

import ast
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ENTRY_POINTS = {
    "bfs": "bfs_dominants",
    "duplicated_greedy": "duplicated_greedy",
    "joint_greedy": "joint_greedy",
    "local_search": "local_search",
    "best_of_all": "dominant",
}


def main():
    project = Path(__file__).resolve().parent
    source = (project / "solution/algorithm.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    entry = tree.body[-1]
    if not isinstance(entry, ast.FunctionDef) or entry.name != "dominant":
        raise ValueError("Expected dominant(g) to be the last definition")
    prefix = "".join(source.splitlines(keepends=True)[:entry.lineno - 1])
    output = project / "submissions"
    output.mkdir(exist_ok=True)
    manifest = {}

    for name, function in ENTRY_POINTS.items():
        if function == "dominant":
            code = source
        else:
            code = prefix + (
                'def dominant(g):\n'
                '    """Codabench entry point: {} strategy."""\n'
                '    return {}(g)\n'
            ).format(name, function)
        ast.parse(code)
        archive = output / (name + ".zip")
        # A fixed timestamp makes identical source produce identical ZIPs.
        member = zipfile.ZipInfo("algorithm.py", date_time=(1980, 1, 1, 0, 0, 0))
        member.compress_type = zipfile.ZIP_DEFLATED
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr(member, code.encode("utf-8"))
        manifest[archive.name] = {
            "entry_point": function,
            "files": ["algorithm.py"],
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        }
        print(archive)

    shutil.copyfile(output / "best_of_all.zip", project / "submission.zip")
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()
