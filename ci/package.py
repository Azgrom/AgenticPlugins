#!/usr/bin/env python3
"""Validate and zip one plugin using only the standard library."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


PACKAGES = {
    'tutor': ('Tutor', 'skills/instructions/scripts/validate_package.py'),
    'devbacklog': ('DevBacklog', 'scripts/validate_package.py'),
}


def main():
    repository = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin', choices=PACKAGES, default='tutor',
                        help='plugin to package (default: tutor)')
    parser.add_argument(
        'output', nargs='?', type=Path,
        help='ZIP destination (default: <repository>/dist/<plugin>.zip)',
    )
    args = parser.parse_args()
    package, validator = PACKAGES[args.plugin]
    source = repository / package
    output = (args.output or repository / 'dist' / f'{args.plugin}.zip').resolve()
    if output.suffix != '.zip':
        parser.error('output must have a .zip extension')
    for package, _ in PACKAGES.values():
        if (repository / package).resolve() in output.parents:
            parser.error(f'output must be outside plugin directories ({package}/)')

    validation = subprocess.run(
        [sys.executable, '-B', validator],
        cwd=source,
    )
    if validation.returncode:
        return validation.returncode

    output.parent.mkdir(parents=True, exist_ok=True)
    archive = shutil.make_archive(str(output.with_suffix('')), 'zip', root_dir=source)
    print(f'Created {archive}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
