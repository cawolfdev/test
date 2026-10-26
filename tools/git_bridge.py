"""Pure Git-object bridge: package tracked files into size-bounded base64 JSON batches.

Usage: python tools/git_bridge.py --out /mnt/data/bridge --max-bytes 6000000
The connector reads each temporary JSON file and submits unchanged base64 blobs to
GitHub's Git Data API. Compare returned sha with expected_git_sha before committing.
Do not commit transfer JSON files; they are transient and contain redundant data.
"""
import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path


def tracked_paths(repo: Path):
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=repo)
    return [x.decode() for x in output.split(b"\0") if x]


def git_blob_sha(data: bytes):
    payload = b"blob " + str(len(data)).encode() + b"\x00" + data
    return hashlib.sha1(payload).hexdigest()


def entry(repo: Path, path: str):
    data = (repo / path).read_bytes()
    return {"path": path, "mode": "100644", "type": "blob", "sha": git_blob_sha(data),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
            "data": base64.b64encode(data).decode("ascii")}


def batches(entries, limit: int):
    group, weight = [], 0
    for record in entries:
        estimated = len(record["data"]) + 400
        if group and weight + estimated > limit:
            yield group
            group, weight = [], 0
        group.append(record)
        weight += estimated
    if group:
        yield group


def export(repo: Path, out: Path, max_bytes: int):
    out.mkdir(parents=True, exist_ok=True)
    entries = [entry(repo, path) for path in tracked_paths(repo)]
    manifest = [{k: e[k] for k in ("path", "mode", "type", "sha", "sha256", "size")} for e in entries]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    for i, group in enumerate(batches(entries, max_bytes), 1):
        (out / f"batch_{i:03d}.json").write_text(json.dumps({"entries": group}, separators=(",", ":")))
    return len(entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-bytes", type=int, default=6_000_000)
    args = parser.parse_args()
    print(f"Packaged {export(Path(__file__).resolve().parents[1], Path(args.out), args.max_bytes)} files")
