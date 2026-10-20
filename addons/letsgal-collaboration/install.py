"""Install a versioned LetsGal collaboration add-on; preview is the default."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import uuid

NAME = "letsgal-collaboration"
MARKER = "<!-- letsgal-collaboration-addon-index -->"


def safe(path):
    p = Path(os.path.abspath(path))
    for item in [*reversed(p.parents), p]:
        if os.path.lexists(item):
            s = item.lstat()
            if stat.S_ISLNK(s.st_mode) or getattr(s, "st_file_attributes", 0) & 0x400:
                raise ValueError("Linked/reparse path is not supported: " + str(item))
    return p


def files(root):
    result = {}
    for folder, dirs, names in os.walk(root, followlinks=False):
        for name in dirs:
            safe(Path(folder) / name)
        for name in names:
            p = safe(Path(folder) / name)
            if not p.is_file():
                raise ValueError("Non-file package entry")
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def identity(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,63}", value) or value.endswith("."):
        raise ValueError("Invalid version")
    if value.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
            *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        raise ValueError("Reserved version")
    return value


def plan(package, skills_root, user_root):
    package, skills_root, user_root = map(safe, (package, skills_root, user_root))
    meta = json.loads(safe(package / "bundle.json").read_text(encoding="utf-8"))
    if meta["name"] != NAME or meta["kind"] != "skill-addon":
        raise ValueError("Unexpected package identity")
    version = identity(meta["version"])
    source = safe(package / "skill")
    for key in meta["files"]:
        p = PurePosixPath(key)
        if p.is_absolute() or ".." in p.parts or "\\" in key or ":" in key:
            raise ValueError("Unsafe manifest path")
    desired = files(source)
    if not desired or desired != meta["files"]:
        raise ValueError("Package payload differs from bundle hashes")
    body = safe(source / "SKILL.md").read_text(encoding="utf-8-sig")
    if not body.startswith("---\n") or f"name: {NAME}\n" not in body:
        raise ValueError("Unexpected Skill frontmatter")
    if not re.search(r"^  version: " + re.escape(version) + r"\s*$", body, re.M):
        raise ValueError("Skill and bundle versions differ")
    main = safe(skills_root / "letsgal-authoring/SKILL.md")
    has_main = main.is_file() and bool(re.search(
        r"^name:\s*['\"]?letsgal-authoring['\"]?\s*$",
        main.read_text(encoding="utf-8-sig"), re.M))
    area = safe(user_root / ".letsgal-authoring")
    target = safe(area / "addons" / NAME / version if has_main else skills_root / NAME)
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and target overlap")
    if target.exists() and not target.is_dir():
        raise ValueError("Target is not a directory")
    existing = files(target) if target.exists() else None
    if existing is not None and existing != desired:
        raise ValueError("Existing Skill differs; preserve and compare it. Nothing overwritten.")
    edits = []
    if has_main:
        index = safe(area / "addons/INDEX.md")
        old = index.read_bytes() if index.exists() else b""
        key = f"| {NAME} | {version} |"
        row = f"{key} [{NAME}]({NAME}/{version}/SKILL.md) | {meta['engine']} | 本地文件已安装；按实际宿主选择 |"
        decoded = old.decode("utf-8-sig")
        if key in decoded:
            if row not in decoded.splitlines():
                raise ValueError("Existing index entry differs; compare it before updating")
            new = old
        else:
            header = "# LetsGal 附加 Skill\n\n按工程实际宿主选择资料，不把最新版本自动设为所有项目默认。\n\n| 名称 | 版本 | 入口 | 宿主证据 | 状态 |\n|---|---|---|---|---|\n"
            new = (old if old else header.encode("utf-8")) + (b"" if not old or old.endswith(b"\n") else b"\n") + (row + "\n").encode("utf-8")
        edits.append((index, old, new))
        preferred = safe(area / "preferences/user.md")
        legacy = safe(area / "user.md")
        profile = preferred if preferred.exists() or not legacy.exists() else legacy
        old = profile.read_bytes() if profile.exists() else b""
        if MARKER in old.decode("utf-8-sig"):
            new = old
        else:
            link = "../addons/INDEX.md" if profile == preferred else "addons/INDEX.md"
            suffix = f"\n\n{MARKER}\n多人实时协作任务：按当前宿主读取[附加 Skill 索引]({link})，再选对应资料；此入口不授权加入房间或扩大写入范围。\n"
            new = old + suffix.encode("utf-8")
        edits.append((profile, old, new))
    return dict(mode="under-main" if has_main else "standalone",
                source=source, target=target, area=area, desired=desired,
                existing=existing, edits=edits, skills_root=skills_root,
                version=version, main_skill_found=has_main)


def install(package, skills_root, user_root, apply=False):
    p = plan(package, skills_root, user_root)
    result = dict(status="PREVIEW", mode=p["mode"], target=str(p["target"]),
                  entry=str(p["target"] / "SKILL.md"), version=p["version"],
                  main_skill_found=p["main_skill_found"], agent_discovery_verified=False,
                  changes=[str(f) for f, old, new in p["edits"] if old != new],
                  payload_change=p["existing"] is None)
    if not apply:
        return result
    lock_root = p["area"] if p["main_skill_found"] else p["skills_root"]
    lock_root.mkdir(parents=True, exist_ok=True)
    lock = safe(lock_root / ".letsgal-collaboration-install.lock")
    # No takeover of another installer's lock, including a stale one.
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))
    try:
        p = plan(package, skills_root, user_root)
        changed = [(f, old, new) for f, old, new in p["edits"] if old != new]
        backup = None
        if any(f.exists() for f, _, _ in changed):
            backup = safe(p["area"] / "backups" / NAME / uuid.uuid4().hex)
            backup.mkdir(parents=True, exist_ok=False)
            for i, (f, old, _) in enumerate(changed):
                if f.exists():
                    dest = backup / f"{i}-{f.name}"
                    dest.write_bytes(old)
                    if dest.read_bytes() != old:
                        raise ValueError("Backup verification failed")
            (backup / "paths.json").write_text(json.dumps(
                {f"{i}-{f.name}": str(f) for i, (f, _, _) in enumerate(changed) if f.exists()},
                ensure_ascii=False, indent=2), encoding="utf-8")
        if p["existing"] is None:
            target = p["target"]
            target.parent.mkdir(parents=True, exist_ok=True)
            staged = safe(target.with_name(target.name + ".install-" + uuid.uuid4().hex))
            shutil.copytree(p["source"], staged)
            if files(staged) != p["desired"]:
                raise ValueError("Staging verification failed; staging retained")
            if target.exists():
                raise ValueError("Target changed during install; staging retained")
            staged.rename(target)
        for f, old, new in changed:
            safe(f)
            if (f.read_bytes() if f.exists() else b"") != old:
                raise ValueError("Routing file changed; copied Skill retained, routing not overwritten")
            f.parent.mkdir(parents=True, exist_ok=True)
            temp = f.with_name(f.name + "." + uuid.uuid4().hex + ".tmp")
            temp.write_bytes(new)
            os.replace(temp, f)
        if files(p["target"]) != p["desired"]:
            raise ValueError("Installed payload verification failed")
        result.update(status="INSTALLED" if p["existing"] is None or changed else "UNCHANGED",
                      backup=str(backup) if backup else None)
        return result
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_skills = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills"
    parser.add_argument("--skills-root", type=Path, default=default_skills)
    parser.add_argument("--user-root", type=Path, default=Path.home())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(Path(__file__).parent, args.skills_root, args.user_root, args.apply),
                         ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"status": "STOPPED", "reason": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
