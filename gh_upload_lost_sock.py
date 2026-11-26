"""Upload main.py + README.md for the Lost Sock entry to GitHub.

Uses the GitHub Contents API: PUT creates the file or updates it when
it already exists (the existing blob sha is sent along). Credentials
come from the surrogate flow for custom.github; nothing secret is
printed or stored here.
"""
import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

OWNER = "rezimtirani"
REPO = "u-eager-stork-81-9647-funniest-lost-sock-status-update-4b1fa3ce-entry"
BRANCH = "main"
API = "https://api.github.com"
ENTRY = Path(
    "/home/hatch/workspace/makefun/u-eager-stork-81-9647-funniest-lost-sock-status-update-4b1fa3ce-entry"
)
FILES = ["main.py", "README.md"]


def github_request(method, url, payload=None):
    body = None
    headers = {"Accept": "application/vnd.github+json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    add_surrogate_to_request(request, "custom.github", allowed_hosts=["api.github.com"])
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def remote_sha(path):
    try:
        info = github_request(
            "GET", f"{API}/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
        )
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    return info.get("sha")


def push_one(path):
    local = ENTRY / path
    encoded = base64.b64encode(local.read_bytes()).decode("ascii")
    payload = {
        "message": f"Add {path} — Lost Sock status update entry",
        "content": encoded,
        "branch": BRANCH,
    }
    sha = remote_sha(path)
    if sha:
        payload["sha"] = sha
    result = github_request(
        "PUT", f"{API}/repos/{OWNER}/{REPO}/contents/{path}", payload
    )
    print(f"{path}: {result['commit']['sha']}")
    return result["commit"]["sha"]


def main():
    parser = argparse.ArgumentParser(description="Upload the Lost Sock entry files.")
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--branch", default=BRANCH)
    args = parser.parse_args()
    print(f"target: {args.owner}/{args.repo}@{args.branch}")
    for name in FILES:
        push_one(name)
    print(f"done: https://github.com/{OWNER}/{REPO}")


if __name__ == "__main__":
    main()
