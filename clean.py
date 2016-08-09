#!/usr/bin/env python2.7
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/clean.py
#=============================================================================#


import argparse, sys, os, re

parser = argparse.ArgumentParser(description='')
parser.add_argument('--noop', action='store_true', default=None, help='Only echo commands.')
parser.add_argument('--debug', action='store_true', default=None, help='Reflect debug information.')
parser.add_argument('files', metavar='FILENAME', type=str, nargs='+', default=None, help='List of files to manipulate.')
args = parser.parse_args()

if not args.files:
    sys.stderr.write('Nothing to do.\n')
    sys.exit(0)

files_skipped = []
files_to_fix = []
path = {}
for f in args.files:
    basename = os.path.basename(f)
    path[basename] = os.path.dirname(f)
    if not os.path.exists(f):
        sys.stderr.write('File not found "{}"'.format(f))
        files_skipped.append(basename)
    else:
        files_to_fix.append(basename)

new_names = {}
for f in files_to_fix:
    replace = re.match(r'^(.*)\.([A-Za-z0-9]{3,4})\Z', f)
    if replace:
        n = replace.group(1) + '.' + replace.group(2).lower()
    else:
        n = f
    # Control characters (+ ? . * ^ $ ( ) [ ] { } | \)
    n = re.sub(r'&', 'and', n)
    n = re.sub(r'\s+\-\s+', '-', n)
    n = re.sub(r'\s+', '_', n)
    n = re.sub(r'\s', '_', n)
    n = re.sub(r'[^A-Za-z0-9_\.\-]', '', n)
    n = re.sub(r'_-', '-', n)
    n = re.sub(r'-_', '-', n)
    n = re.sub(r'_{2,}', '_', n)
    new_names[f] = n

for f in files_to_fix:
    oldname = f
    newname = new_names[f]
    if len(path[f]) > 0:
        oldname = path[f] + '/' + f
        newname = path[f] + '/' + new_names[f]
    if f != new_names[f]:
        sys.stderr.write('"{}" -> "{}"'.format(oldname, newname))
        if not args.noop: os.rename(oldname, newname)
    if not args.noop and os.path.isfile(newname):
        os.chmod(newname, 0644)

