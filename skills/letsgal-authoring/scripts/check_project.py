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
    unsupported_chapters = 0
    unsupported_blocks = 0
    unchecked_blocks = 0

    def issue(level, where, message, code=None):
        row = {"level": level, "location": where, "message": message}
        if code:
            row['code'] = code
        issues.append(row)

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

    def chapter(path, is_entry=False, in_linear_order=False):
        nonlocal chapters_checked, unsupported_chapters, unsupported_blocks, unchecked_blocks
        where = path.name
        try:
            data = read(path)
        except (OSError, ValueError) as exc:
            issue("error", where, str(exc))
            return
        chapters_checked += 1
        if format_profile == 'auto' and (not isinstance(data, dict) or 'fragments' not in data):
            unsupported_chapters += 1
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
        if in_linear_order and data.get('kind') == 'schedule-preprocessing':
            issue('warning', where, 'schedule-preprocessing chapter is listed in ordinary chapterOrder; official scheduling excludes preprocessing from the linear order; inspect target-version indexing before changing source',
                  'preprocessing_in_linear_order')
        fragments = data.get("fragments")
        if not isinstance(fragments, list) or not fragments:
            issue("error", where, "fragments must be a non-empty array")
            return
        ids = {f.get("id") for f in fragments if isinstance(f, dict) and isinstance(f.get("id"), str)}
        main = fragments[0].get("id") if isinstance(fragments[0], dict) else None
        edges = {key: set() for key in ids}

        def ref(value, loc, origin, allow_empty=False, call_fragment=False):
            if allow_empty and value == "":
                return
            if not isinstance(value, str) or value not in ids:
                issue("error", loc, "target must be an existing same-chapter fragment id")
                return
            if value == main:
                if call_fragment:
                    issue("warning", loc, "callFragment targeting main: official JSON reference and Call Fragment guide differ; noncyclic A-to-main executed and returned in 2.3.0-beta.1 native fragment preview; other hosts, entry paths and exports require their own evidence; preserve existing references",
                          'main_call_version_sensitive')
                else:
                    issue("error", loc, "branch/if target must be a non-main fragment id in the documented subset")
                    return
            if origin in edges:
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
                    unchecked_blocks += 1
                    issue("warning", bl, "instruction is outside this checker's supported subset; consult official reference")
                if not isinstance(props, dict):
                    issue("error", bl, "props must be an object")
                    continue
                required_parameter = {'branch':'choices','if':'conditions','callFragment':'fragmentId','setver':'key'}.get(kind) if isinstance(kind,str) else None
                if format_profile == 'auto' and required_parameter and required_parameter not in props:
                    unsupported_blocks += 1
                    issue('warning', bl, 'instruction parameters do not match the documented subset; verify target-version serialization before treating this as an error')
                    continue
                if "disabled" in props and not isinstance(props["disabled"], bool):
                    issue("error", bl, "props.disabled must be boolean")
                if block.get("children"):
                    issue("warning", bl, "nested children are not checked; do not model branch targets here")
                if isinstance(kind, str) and kind in TEXT:
                    content = block.get("content")
                    if kind == "narration" and "content" not in block and format_profile == "auto":
                        issue("warning", bl, "native empty narration may omit content (observed in 2.4.0-beta.1); confirm the intended blank, text and runtime are not verified", "native_empty_narration")
                    elif not isinstance(content, list):
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
                    if props.get('fragmentId') == '' and format_profile == 'auto':
                        issue('warning', bl, 'empty callFragment target is a documented editor no-op; select a real target for generated playable content')
                    else:
                        ref(props.get("fragmentId"), bl, origin, call_fragment=True)
                elif kind == "setver":
                    if not isinstance(props.get("key"), str) or not props["key"]:
                        issue("error", bl, "assignment requires variable key")
                    issue("warning", bl, "assignment operands and variable declarations are not validated")
        # Iterative traversal avoids Python recursion on long, valid chapter chains.
        state = {}
        has_cycle = False
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
                    has_cycle = True
                elif not state.get(dest):
                    state[dest] = 1
                    stack.append((dest, iter(edges[dest])))
        if has_cycle:
            issue('warning', where, 'cycle in stored fragment references: official conversion-time 30-layer expansion description differed from three 2.3.0-beta.1 native cases, whose cycle back-edges did not repeat; not a runtime recursion guarantee; this checker does not infer disabled instructions or reachability',
                  'fragment_cycle')
        # Kahn traversal also checks independent acyclic components/prefixes when
        # another component contains a cycle. Nodes held by cycles are not a
        # runtime trace or a complete longest-path analysis of a cyclic graph.
        indegree = {node:0 for node in edges}
        depth = {node:0 for node in edges}
        for links in edges.values():
            for dest in links: indegree[dest] += 1
        pending = [node for node,count in indegree.items() if count == 0]
        while pending:
            node = pending.pop()
            for dest in edges[node]:
                depth[dest] = max(depth[dest], depth[node]+1)
                indegree[dest] -= 1
                if indegree[dest] == 0: pending.append(dest)
        if max(depth.values(), default=0) > 30:
            issue('warning', where, 'acyclic stored-reference depth exceeds the documented 30-level expansion threshold; this is a diagnostic heuristic, not a measured hard limit; verify target-host conversion separately',
                  'fragment_depth')

    target = safe_path(target)
    if target.is_file():
        chapter(target)
        issue("warning", target.name, "standalone chapter: project index and global uniqueness not verified")
    else:
        project = read(target / "project.json")
        if format_profile == 'auto' and (not isinstance(project, dict) or 'chapterOrder' not in project):
            return {'status':'unsupported_format','errors':0,'warnings':1,'chapters_checked':0,
                    'unsupported_project':True,'read_only':True,'format_profile':format_profile,'engine_compatibility':'not_verified',
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
            chapter(root / (name + ".json"), is_entry=(i == 0), in_linear_order=True)
        for path in sorted(root.glob("*.json")):
            if path.stem not in names:
                try:
                    preprocessing = isinstance(data := read(path), dict) and data.get('kind') == 'schedule-preprocessing'
                except (OSError, ValueError):
                    preprocessing = False
                if not preprocessing:
                    issue("warning", path.name, "chapter file is not listed in chapterOrder; inspect before integrating")
                chapter(path)
        issue("warning", "project", "blueprint routes, chapter tree, asset/character/variable references and runtime are not checked")
    errors = sum(i["level"] == "error" for i in issues)
    return {"status": "issues_found" if errors else ("unsupported_format" if unsupported_chapters or unsupported_blocks else "partial_static_checks_passed"),
            "chapters_checked": chapters_checked, "errors": errors,
            "unsupported_chapters": unsupported_chapters, "unsupported_blocks": unsupported_blocks,
            "unchecked_blocks": unchecked_blocks, "format_profile": format_profile, "read_only":True,
            "engine_compatibility": "not_verified",
            "schema_basis": "authoring-subset-v0.1.4",
            "warnings": sum(i["level"] == "warning" for i in issues),
            "scope": "Read-only subset; not full parameter/type/asset/variable validation, a compiler, engine load or runtime-flow acceptance.",
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
