"""Explicit, portable release file selection. Never collect an entire workspace."""
import json
from pathlib import Path, PurePosixPath
import stat

def release_files(root):
    root=Path(root).absolute()
    listing=json.loads((root/'release-files.json').read_text('utf-8'))
    if listing.get('schema') != 1 or not isinstance(listing.get('files'),list):
        raise ValueError('Unsupported release file list')
    selected=[]
    names=set()
    for name in listing['files']:
        if not isinstance(name,str) or not name or '\\' in name or ':' in name:
            raise ValueError('Invalid release path')
        parts=PurePosixPath(name).parts
        if name.startswith('/') or any(part in ('..','.') for part in parts) or '/'.join(parts)!=name:
            raise ValueError('Unsafe release path')
        if any(part.startswith('.') for part in parts) and name not in ('.gitignore','.gitattributes'):
            raise ValueError('Hidden runtime/configuration content is not distributable')
        if name.lower() in names:
            raise ValueError('Duplicate release path')
        names.add(name.lower())
        path=root.joinpath(*parts)
        for ancestor in [path,*path.parents]:
            info=ancestor.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                raise ValueError('Linked release content is not supported')
            if ancestor==root:
                break
        if not path.is_file():
            raise ValueError('Release entry must be a regular file')
        selected.append(path)
    if 'release-files.json' not in names or 'sha256sums.txt' not in names:
        raise ValueError('Release list must include itself and the checksum file')
    return sorted(selected)
