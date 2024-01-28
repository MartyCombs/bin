#!/usr/bin/env python3
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-number.py
#=============================================================================#

import argparse
import sys
import os
import re

class NumberPics:
    filename_format = re.compile(r'^(\S+)\-(\d+)\.([A-Za-z0-9]{1,4})\Z')
    anyfile_format = re.compile(r'^(\S+)\.([A-Za-z0-9]{1,4})\Z')
    ''' Files are named as:

        BASE-NUM.EXT where
            BASE - Base name for all files.
            NUM  - A number with potential leading zeros.
            EXT  - The file extension.

        where bob.mp4 and bob.png must have different numbers.
    '''
    def __init__(self, debug=False, noop=False, prepend=False, nameformat=None, srcfiles=None):
        self.debug = debug
        self.noop = noop
        self.prepend = prepend
        self.nameformat = nameformat
        self.srcfiles = srcfiles
        self.intermediates = {}
        self.new_names = {}
    def parts(self, filename):
        fullname = os.path.abspath(filename)
        f = {'base' : None, 'n' : None, 'ext' : None }
        basename = os.path.basename(fullname)

        match_format = re.match(NumberPics.filename_format, basename)
        match_anyfile = re.match(NumberPics.anyfile_format, basename)
        if match_format:
            (f['base'], f['n'], f['ext']) = (match_format.group(1), match_format.group(2), match_format.group(3))
        else:
            (f['base'], f['n'], f['ext']) = (match_anyfile.group(1), None, match_anyfile.group(2))
        return f
    def create_new_names(self):
        filecount = str(len(self.srcfiles))
        digits = len(filecount)
        n = 0
        for f in self.srcfiles:
            n += 1
            p = self.parts(f)
            new_name = str(self.nameformat) + '-' + str(n).zfill(digits) + '.' + p['ext'].lower()
            if f == new_name:
                self.new_names[f] = new_name
            elif new_name in self.srcfiles:
                intermediate = 'int-' + new_name
                self.intermediates[intermediate] = new_name
                self.new_names[f] = intermediate
            else:
                self.new_names[f] = new_name
    def rename_files(self):
        for f in self.new_names:
            if f == self.new_names[f]:
                if self.debug:
                    print('{} REMAINS'.format(f))
            else:
                print('{} -> {}'.format(f, self.new_names[f]))
                if self.noop == False:
                    os.rename(f, self.new_names[f])
        for i in self.intermediates:
            print('{} -> {}'.format(i, self.intermediates[i]))
            if self.noop == False:
                os.rename(i, self.intermediates[i])


def main():
    parser = argparse.ArgumentParser(description='None')
    parser.add_argument('--debug', action='store_true', default=False, help='')
    parser.add_argument('--noop', action='store_true', default=False, help='')
    parser.add_argument('--prepend', action='store_true', default=False, help='')
    parser.add_argument('nameformat', type=str, nargs='?', default=None, help='')
    parser.add_argument('srcfiles', type=str, nargs='*', default=None, help='')
    args = parser.parse_args()

    s = NumberPics(debug=args.debug, noop=args.noop, prepend=args.prepend, nameformat=args.nameformat, srcfiles=args.srcfiles)
    s.create_new_names()
    s.rename_files()

if __name__ == "__main__":
    main()
