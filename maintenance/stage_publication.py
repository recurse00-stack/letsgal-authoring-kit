"""Copy the explicitly approved core and workshop source into a NEW publication staging directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from build_workshop import ordinary, overlaps, source_files
from release_manifest import release_files
from review_release import audit, inspect_text


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
    listing = ordinary(root / 'workshop-source-files.json')
    if inspect_text(listing.read_text('utf-8'), [os.environ.get('USERNAME', '')]):
        raise ValueError('Workshop manifest privacy review failed')
    files = sorted(set(release_files(root) + source_files(root) + [listing]))
    out.mkdir(parents=True)
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
