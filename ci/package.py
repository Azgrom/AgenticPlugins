#!/usr/bin/env python3
"""Validate and zip the contents of src/ using only the standard library."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    repository = Path(__file__).resolve().parent.parent
    source = repository / 'src'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'output', nargs='?', type=Path,
        default=repository / 'dist' / 'tutor.zip',
        help='ZIP destination (default: <repository>/dist/tutor.zip)',
    )
    output = parser.parse_args().output.resolve()
    if output.suffix != '.zip':
        parser.error('output must have a .zip extension')
    if source in output.parents:
        parser.error('output must be outside src/')

    validation = subprocess.run(
        [sys.executable, '-B', 'skills/instructions/scripts/validate_package.py'],
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
