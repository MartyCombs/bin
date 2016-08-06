#!/usr/bin/env python2.7
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/clean.py
#=============================================================================#


import argparse, sys, os, re

parser = argparse.ArgumentParser(description='')
parser.add_argument('--debug', action='store_true', help='Reflect debug information.')
parser.add_argument('files', metavar='FILENAME', type=str, nargs='+', default=None, help='List of files to manipulate.')
args = parser.parse_args()

files_skipped = []
files_to_fix = []
for f in args.files:
    if not os.path.exists(f):
        sys.stderr.write('File not found "{}"'.format(f))
        files_skipped.append(f)
    else:
        files_to_fix.append(f)

new_names = {}
for f in files_to_fix:
    replace = re.match(r'^([\S+\s+])\.([A-Za-z0-9]{3,4})\Z', f)
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
    if f != new_names[f]:
        print '"{}" -> "{}"'.format(f, new_names[f])
        os.rename(f, new_names[f])
    if os.path.isfile(new_names[f]):
        os.chmod(new_names[f], 0644)

