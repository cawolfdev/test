"""Create a fully portable, versioned archive including local git history."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def package_workspace(root, destination):
    root=Path(root).resolve()
    destination=Path(destination).resolve()
    destination.parent.mkdir(parents=True,exist_ok=True)
    ignore_dirs={'__pycache__','.pytest_cache'}
    with ZipFile(destination,'w',ZIP_DEFLATED,compresslevel=6) as zf:
        for file in sorted(root.rglob('*')):
            if not file.is_file() or file==destination:
                continue
            if any(part in ignore_dirs for part in file.relative_to(root).parts) or file.suffix=='.pyc':
                continue
            zf.write(file,arcname=str(Path(root.name)/file.relative_to(root)))
    return destination
