"""Copy only approved community source into a NEW publication staging directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
from release_manifest import release_files
from review_release import audit


def ordinary(path):
    path = Path(path).absolute()
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Linked staging paths are not supported')
    return Path(os.path.abspath(path))


def overlaps(left, right):
    return left == right or left in right.parents or right in left.parents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = ordinary(args.output)
    if out.exists() or overlaps(root, out):
        parser.error('Output must be a NEW directory outside source')
    if audit(root, [os.environ.get('USERNAME', '')])['status'] != 'passed':
        raise ValueError('Core privacy review failed')
    files = release_files(root)
    out.mkdir(parents=True, exist_ok=False)
    for source in files:
        target = out / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if target.read_bytes() != source.read_bytes():
            raise ValueError('Staging readback failed')
    digest = hashlib.sha256()
    for source in files:
        digest.update(source.relative_to(root).as_posix().encode() + b'\0' + source.read_bytes() + b'\0')
    print(json.dumps({'files': len(files), 'content_sha256': digest.hexdigest(),
                      'scope': 'Source staging only. No commit, push, tag or release performed.'}))


if __name__ == '__main__':
    main()
