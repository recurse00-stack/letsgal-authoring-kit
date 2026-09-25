"""Read-only, partial checks for LetsGal chapter source JSON. Python 3.9+."""
import argparse
import json
import stat
import sys
from pathlib import Path

MAX_BYTES = 16 * 1024 * 1024
KNOWN = {"narration", "dialogue", "storyParagraph", "comment", "branch", "if",
         "callFragment", "setver", "wait", "endChapter"}
TEXT = {"narration", "dialogue", "storyParagraph", "comment"}


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def no_constant(_value):
    raise ValueError("non-finite JSON number")


def parse(text):
    return json.loads(text, object_pairs_hook=pairs, parse_constant=no_constant)


def safe_path(path):
    path = path.absolute()
    for item in [path, *path.parents]:
        if item.exists() or item.is_symlink():
            info = item.lstat()
            if item.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("symlink or reparse point is not supported")
    return path.resolve(strict=True)


def read(path):
    path = safe_path(path)
    if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size > MAX_BYTES:
        raise ValueError("expected regular JSON file no larger than 16 MiB")
    try:
        return parse(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line %d column %d" % (exc.lineno, exc.colno)) from None
    except RecursionError:
        raise ValueError("JSON nesting too deep") from None


def check(target, format_profile='auto'):
    issues = []
    seen_ids = set()
    chapters_checked = 0
    unsupported = 0

    def issue(level, where, message):
        issues.append({"level": level, "location": where, "message": message})

    def identity(value, where, required=True):
        if value is None and not required:
            return
        if not isinstance(value, str) or not value:
            issue("error", where, "missing or invalid id")
        elif value in seen_ids:
            issue("error", where, "duplicate id across inspected source objects")
        else:
            seen_ids.add(value)

    def embedded(props, key, where, expected=list):
        value = props.get(key)
        if not isinstance(value, str):
            issue("error", where, key + " must be a JSON string")
            return None
        try:
            decoded = parse(value)
        except (ValueError, RecursionError):
            issue("error", where, key + " contains invalid JSON")
            return None
        if not isinstance(decoded, expected):
            issue("error", where, key + " has wrong decoded shape")
            return None
        return decoded

    def chapter(path, is_entry=False):
        nonlocal chapters_checked, unsupported
        where = path.name
        try:
            data = read(path)
        except (OSError, ValueError) as exc:
            issue("error", where, str(exc))
            return
        chapters_checked += 1
        if format_profile == 'auto' and (not isinstance(data, dict) or 'fragments' not in data):
            unsupported += 1
            issue('warning', where, 'unrecognized chapter format; no conversion attempted; verify the target Studio version and a chapter saved by that version')
            return
        if not isinstance(data, dict):
            issue("error", where, "chapter must be an object")
            return
        identity(data.get("id"), where)
        if data.get("name") != path.stem:
            issue("error", where, "chapter name must match filename")
        if "disabled" in data and not isinstance(data["disabled"], bool):
            issue("error", where, "chapter disabled must be boolean")
        if is_entry and data.get("disabled") is True:
            issue("error", where, "entry chapter is disabled")
        fragments = data.get("fragments")
        if not isinstance(fragments, list) or not fragments:
            issue("error", where, "fragments must be a non-empty array")
            return
        ids = {f.get("id") for f in fragments if isinstance(f, dict) and isinstance(f.get("id"), str)}
        main = fragments[0].get("id") if isinstance(fragments[0], dict) else None
        edges = {key: set() for key in ids}

        def ref(value, loc, origin, allow_empty=False):
            if allow_empty and value == "":
                return
            if not isinstance(value, str) or value not in ids or value == main:
                issue("error", loc, "target must be an existing same-chapter non-main fragment id")
            elif origin in edges:
                edges[origin].add(value)

        for fi, fragment in enumerate(fragments):
            loc = where + ":fragments[%d]" % fi
            if not isinstance(fragment, dict):
                issue("error", loc, "fragment must be an object")
                continue
            identity(fragment.get("id"), loc)
            name = fragment.get("name")
            if not isinstance(name, str) or not name or (fi == 0 and name != "main") or (fi > 0 and name == "main"):
                issue("error", loc, "first fragment must be main; others need a different non-empty name")
            if "metadata" in fragment and not isinstance(fragment["metadata"], dict):
                issue("error", loc, "metadata must be an object")
            blocks = fragment.get("blocks")
            if not isinstance(blocks, list):
                issue("error", loc, "blocks must be an array")
                continue
            for bi, block in enumerate(blocks):
                bl = loc + ".blocks[%d]" % bi
                if not isinstance(block, dict):
                    issue("error", bl, "block must be an object")
                    continue
                identity(block.get("id"), bl, required=False)
                kind, props = block.get("type"), block.get("props")
                if not isinstance(kind, str) or not kind:
                    issue("error", bl, "type must be a non-empty string")
                elif kind not in KNOWN:
                    issue("warning", bl, "instruction is outside this checker's supported subset; consult official reference")
                if not isinstance(props, dict):
                    issue("error", bl, "props must be an object")
                    continue
                required_parameter = {'branch':'choices','if':'conditions','callFragment':'fragmentId','setver':'key'}.get(kind) if isinstance(kind,str) else None
                if format_profile == 'auto' and required_parameter and required_parameter not in props:
                    unsupported += 1
                    issue('warning', bl, 'instruction parameters do not match the documented subset; verify target-version serialization before treating this as an error')
                    continue
                if "disabled" in props and not isinstance(props["disabled"], bool):
                    issue("error", bl, "props.disabled must be boolean")
                if block.get("children"):
                    issue("warning", bl, "nested children are not checked; do not model branch targets here")
                if isinstance(kind, str) and kind in TEXT:
                    content = block.get("content")
                    if not isinstance(content, list):
                        issue("error", bl, "text-bearing instruction needs a content array")
                    else:
                        for inline in content:
                            if not isinstance(inline, dict):
                                issue("error", bl, "inline content must be an object")
                            elif inline.get("type") == "text" and (not isinstance(inline.get("text"), str) or not isinstance(inline.get("styles"), dict)):
                                issue("error", bl, "text inline needs string text and object styles")
                            elif inline.get("type") != "text":
                                issue("warning", bl, "non-text inline content not validated")
                origin = fragment.get("id")
                if not isinstance(origin, str):
                    origin = None
                if kind == "branch":
                    choices = embedded(props, "choices", bl)
                    if choices == []:
                        issue("error", bl, "playable branch needs choices")
                    defaults = 0
                    for ci, choice in enumerate(choices or []):
                        cl = bl + ".choices[%d]" % ci
                        if not isinstance(choice, dict):
                            issue("error", cl, "choice must be an object")
                            continue
                        if not isinstance(choice.get("text"), str) or not choice["text"].strip():
                            issue("error", cl, "choice requires visible text")
                        if "isDefault" in choice and not isinstance(choice["isDefault"], bool):
                            issue("error", cl, "isDefault must be boolean")
                        defaults += choice.get("isDefault") is True
                        mode = choice.get("mode")
                        if "mode" not in choice and format_profile == 'auto':
                            mode = 'jump'
                            issue("warning", cl, "legacy choice omits mode; inspected using the documented jump default, without modifying source")
                        if mode == "jump":
                            ref(choice.get("fragmentId"), cl, origin, True)
                        elif mode == "vars":
                            if not isinstance(choice.get("varOps"), list):
                                issue("error", cl, "vars choice requires varOps array")
                            else:
                                issue("warning", cl, "variable operations and keys require project-specific validation")
                        else:
                            issue("error", cl, "new choice requires jump or vars mode")
                    if defaults > 1:
                        issue("error", bl, "only one default choice allowed")
                elif kind == "if":
                    embedded(props, "conditions", bl)
                    ref(props.get("thenFragmentId"), bl, origin)
                    ref(props.get("elseFragmentId", ""), bl, origin, True)
                    if props.get("logicOp", "and") not in ("and", "or"):
                        issue("error", bl, "invalid logicOp")
                    issue("warning", bl, "condition expression fields, types and variables need semantic validation")
                elif kind == "callFragment":
                    ref(props.get("fragmentId"), bl, origin)
                elif kind == "setver":
                    if not isinstance(props.get("key"), str) or not props["key"]:
                        issue("error", bl, "assignment requires variable key")
                    issue("warning", bl, "assignment operands and variable declarations are not validated")
        # Iterative traversal avoids Python recursion on long, valid chapter chains.
        state = {}
        for start in edges:
            if state.get(start):
                continue
            stack = [(start, iter(edges[start]))]
            state[start] = 1
            while stack:
                node, links = stack[-1]
                dest = next(links, None)
                if dest is None:
                    state[node] = 2
                    stack.pop()
                elif state.get(dest) == 1:
                    issue("error", where, "fragment call cycle detected; remove recursion or review actual flow")
                elif not state.get(dest):
                    state[dest] = 1
                    stack.append((dest, iter(edges[dest])))

    target = safe_path(target)
    if target.is_file():
        chapter(target)
        issue("warning", target.name, "standalone chapter: project index and global uniqueness not verified")
    else:
        project = read(target / "project.json")
        if format_profile == 'auto' and (not isinstance(project, dict) or 'chapterOrder' not in project):
            return {'status':'unsupported_format','errors':0,'warnings':1,'chapters_checked':0,
                    'unsupported_project':True,'format_profile':format_profile,'engine_compatibility':'not_verified',
                    'issues':[{'level':'warning','location':'project.json','message':'unrecognized project index; verify the target Studio version; no conversion attempted'}]}
        if not isinstance(project, dict):
            raise ValueError("project.json must contain an object")
        order = project.get("chapterOrder")
        if not isinstance(order, list) or not order:
            issue("error", "project.json", "chapterOrder must be a non-empty array")
            order = []
        names = set()
        root = safe_path(target / "chapters")
        if not root.is_dir():
            raise ValueError("chapters must be a directory")
        for i, name in enumerate(order):
            if not isinstance(name, str) or not name or name in (".", "..") or any(c in name for c in '/\\:\x00'):
                issue("error", "project.json", "invalid chapter name in index")
                continue
            if name in names:
                issue("error", "project.json", "duplicate chapter name in index")
                continue
            names.add(name)
            chapter(root / (name + ".json"), is_entry=(i == 0))
        for path in sorted(root.glob("*.json")):
            if path.stem not in names:
                issue("warning", path.name, "chapter file is not listed in chapterOrder; inspect before integrating")
                chapter(path)
        issue("warning", "project", "blueprint routes, chapter tree, asset/character/variable references and runtime are not checked")
    errors = sum(i["level"] == "error" for i in issues)
    return {"status": "issues_found" if errors else ("unsupported_format" if unsupported else "partial_static_checks_passed"),
            "chapters_checked": chapters_checked, "errors": errors,
            "unsupported_chapters": unsupported, "format_profile": format_profile,
            "engine_compatibility": "not_verified",
            "schema_basis": "Documented fragment subset; compare target-version samples before applying findings.",
            "warnings": sum(i["level"] == "warning" for i in issues),
            "scope": "Read-only subset; not a full schema, compiler, engine load or runtime acceptance.",
            "issues": issues}


def syntax_check(target):
    """Parse only explicitly scoped project/chapter JSON; do not impose an engine schema."""
    target = safe_path(target)
    files = [target] if target.is_file() else [target / 'project.json']
    if target.is_dir() and (target / 'chapters').exists():
        root = safe_path(target / 'chapters')
        files.extend(sorted(root.glob('*.json')))
    issues = []
    for path in files:
        try:
            read(path)
        except (OSError, ValueError) as exc:
            issues.append({'level':'error', 'location':path.name, 'message':str(exc)})
    return {'status':'issues_found' if issues else 'json_syntax_passed', 'errors':len(issues),
            'files_checked':len(files), 'format_profile':'json-only', 'read_only':True,
            'engine_compatibility':'not_verified', 'issues':issues,
            'scope':'JSON syntax only; no field, schema, stable/beta feature or runtime compatibility claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument('--format', choices=['auto','fragments','json-only'], default='auto',
                        help='auto recognizes the documented fragment layout; json-only avoids applying that schema to older or unknown formats')
    args = parser.parse_args()
    try:
        result = syntax_check(args.path) if args.format == 'json-only' else check(args.path, args.format)
        code = 1 if result['errors'] else (2 if result.get('status') == 'unsupported_format' else 0)
    except (OSError, ValueError, RecursionError) as exc:
        result = {"status": "cannot_check", "error": str(exc), "read_only": True}
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
