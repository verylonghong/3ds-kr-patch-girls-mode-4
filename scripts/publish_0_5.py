"""Publish the two approved 0.5 patch assets after local and remote hash checks."""

import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ASSETS = {
    "GS4_Korean_v0.5_From_Japan_3DS.xdelta": (
        4769398,
        "650852098920ebbf5833bbdfb86213a254d01021c4808db5776e4eb22d5c3f4e",
    ),
    "GS4_Korean_Repack_v0.5.zip": (
        12972252,
        "2ce848fc3d882262b4222c73191c23ce350753dc43b8d48a6297f2498d8f0dc9",
    ),
}


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    if repo != "verylonghong/3ds-kr-patch-girls-mode-4":
        raise RuntimeError("Unexpected repository")
    token = os.environ["GH_TOKEN"]
    endpoint = f"https://api.github.com/repos/{repo}/releases"

    def api(url, method="GET", body=None, binary=None):
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gs4-korean-release-0.5",
        }
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if binary is not None:
            data = binary
            headers["Content-Type"] = "application/octet-stream"
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=120) as response:
            return json.load(response)

    payloads = {}
    for name, (size, digest) in ASSETS.items():
        data = (Path("patches/0.5") / name).read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
            raise RuntimeError(f"Local asset verification failed: {name}")
        payloads[name] = data

    try:
        release = api(endpoint + "/tags/v0.5")
    except HTTPError as error:
        if error.code != 404:
            raise
        release = api(endpoint, "POST", {
            "tag_name": "v0.5",
            "target_commitish": os.environ["GITHUB_SHA"],
            "name": "걸스 모드 4 한국어 패치 0.5",
            "body": Path("RELEASE_NOTES.md").read_text(encoding="utf-8"),
            "draft": True,
            "prerelease": False,
        })

    release_url = endpoint + "/" + str(release["id"])
    existing = {asset["name"]: asset for asset in release["assets"]}
    if set(existing) - set(ASSETS):
        raise RuntimeError("Unexpected remote assets; release left unchanged")
    for name, data in payloads.items():
        if name in existing:
            continue
        if not release["draft"]:
            raise RuntimeError("Published release has missing assets; left unchanged")
        upload_url = release["upload_url"].split("{", 1)[0]
        api(upload_url + "?name=" + quote(name), "POST", binary=data)

    def verify(remote):
        assets = {asset["name"]: asset for asset in remote["assets"]}
        if len(remote["assets"]) != 2 or set(assets) != set(ASSETS):
            raise RuntimeError("Remote asset count mismatch")
        for name, (size, digest) in ASSETS.items():
            asset = assets[name]
            if asset["size"] != size or asset.get("digest") != "sha256:" + digest:
                raise RuntimeError(f"Remote asset verification failed: {name}")

    release = api(release_url)
    verify(release)
    notes = Path("RELEASE_NOTES.md").read_text(encoding="utf-8")
    if release.get("body") != notes:
        release = api(release_url, "PATCH", {"body": notes})
    if release["draft"]:
        release = api(release_url, "PATCH", {"draft": False})
    verify(release)
    if release["draft"]:
        raise RuntimeError("Release is still a draft")
    print(json.dumps({
        "release_url": release["html_url"],
        "assets": [{"name": a["name"], "size": a["size"], "digest": a["digest"]} for a in release["assets"]],
        "published": True,
    }, indent=2))
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write(f"Published [v0.5]({release['html_url']}) with two verified patch assets.\n")


if __name__ == "__main__":
    main()
