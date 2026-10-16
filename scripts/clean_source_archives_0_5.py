"""Point v0.5 source archives at the commit without tracked patch payloads."""

import json
import os
from urllib.request import Request, urlopen


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    if repo != "verylonghong/3ds-kr-patch-girls-mode-4":
        raise RuntimeError("Unexpected repository")
    target = os.environ["GITHUB_SHA"]
    root = f"https://api.github.com/repos/{repo}"

    def api(path, method="GET", body=None):
        headers = {
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gs4-source-archive-cleanup",
        }
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        with urlopen(Request(root + path, data=data, headers=headers, method=method), timeout=60) as response:
            return json.load(response)

    expected_assets = {
        "GS4_Korean_v0.5_From_Japan_3DS.xdelta": (
            647874958, 4769398,
            "sha256:650852098920ebbf5833bbdfb86213a254d01021c4808db5776e4eb22d5c3f4e",
        ),
        "GS4_Korean_Repack_v0.5.zip": (
            647875044, 12972252,
            "sha256:2ce848fc3d882262b4222c73191c23ce350753dc43b8d48a6297f2498d8f0dc9",
        ),
    }

    def verify_release(release):
        if release["id"] != 415151611 or release["draft"]:
            raise RuntimeError("Unexpected release")
        assets = {asset["name"]: (asset["id"], asset["size"], asset.get("digest")) for asset in release["assets"]}
        if assets != expected_assets:
            raise RuntimeError("Release attachments changed; stopping")

    release = api("/releases/tags/v0.5")
    verify_release(release)
    if release.get("immutable"):
        raise RuntimeError("Release is immutable; source tag cannot be changed")
    tree = api(f"/git/trees/{target}?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("Incomplete source tree")
    paths = [item["path"] for item in tree["tree"] if item["type"] == "blob"]
    if any(path.endswith(".xdelta") or path.endswith("GS4_Korean_Repack_v0.5.zip") for path in paths):
        raise RuntimeError("Patch payload is still present in source tree")
    tag = api("/git/ref/tags/v0.5")
    previous = "d067e25b498ed21f0132dca977a356608807e7a5"
    if tag["object"]["type"] != "commit" or tag["object"]["sha"] not in (previous, target):
        raise RuntimeError("Source tag changed unexpectedly; stopping")
    if tag["object"]["sha"] != target:
        api("/git/refs/tags/v0.5", "PATCH", {"sha": target, "force": True})
    if api("/git/ref/tags/v0.5")["object"]["sha"] != target:
        raise RuntimeError("Source tag update did not apply")
    verify_release(api("/releases/tags/v0.5"))
    print(json.dumps({"tag": "v0.5", "commit": target, "tracked_patch_payloads": 0, "release_attachments_unchanged": True}))


if __name__ == "__main__":
    main()
