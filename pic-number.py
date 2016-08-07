#!/usr/bin/env python2.7
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-number.py
#=============================================================================#

'''
Given a regular expression, adjust file names to match the regular expression.
'''
import argparse, sys, os, fnmatch, re, tempfile

class NumberPics:
    def __init__(self, debug=False, noop=False, prepend=False, nameformat=None):
        self.debug = debug
        self.noop = noop
        self.prepend = prepend
        self.nameformat = nameformat
        self.base_directory = {}
        self.filenames_to_change = []
        self.filenames_skipped = []
        self.filenames_already_matching = []
        self.filename_format = re.compile(r'^(\S+)\-\d+\.([A-Za-z0-9]{3,4})\Z')
        self.total_files = 0
        self.num_digits = 0
        self.files = {}


    def build_list(self, filelist=None):
        to_skip = []
        already_matching = []
        to_change = []
        path = {}
        for f in sorted(filelist):
            basename = os.path.basename(f)
            path[basename] = os.path.dirname(f)
            # Skip any files which begin with a dot as they may be thumbnails.
            if basename.startswith('.'):
                to_skip.append(basename)
                continue
            if fnmatch.fnmatch(basename, self.nameformat + '*'):
                already_matching.append(basename)
            else:
                to_change.append(basename)
        self.filenames_to_change = to_change
        self.filenames_already_matching = already_matching
        self.filenames_skipped = to_skip
        self.base_directory = path
        self.total_files = len(self.filenames_already_matching) + len(self.filenames_to_change)
        self.num_digits = len(str(self.total_files))


    def replace_files(self, files=None, replace_with=None, index=None, digits=0):
        if index < 1: return index
        for f in sorted(files, reverse=True):
            oldname = f
            if replace_with:
                replace = re.match(r'^(\S+)\.([A-Za-z0-9]{3,4})\Z', f)
                newname = replace_with + '-' + str(index).zfill(digits) + '.' + replace.group(2).lower()
            else:
                if re.match(self.filename_format, f):
                    replace_digits = re.match(r'^(\S+)\-\d+\.([A-Za-z0-9]{3,4})\Z', f)
                    newname = replace_digits.group(1) + '-' + str(index).zfill(digits) + '.' + replace_digits.group(2).lower()
                else:
                    keep = re.match(r'^(\S+)\.([A-Za-z0-9]{3,4})\Z', f)
                    newname = keep.group(1) + '-' + str(index).zfill(digits) + '.' + keep.group(2).lower()
            if len(self.base_directory[f]) > 0:
                oldname = self.base_directory[f] + '/' + f
                newname = self.base_directory[f] + '/' + newname
            self.files[oldname] = newname
            index -= 1
        return index


    def update_files(self, files=None):
        for f in sorted(files.keys()):
            if f == files[f]:
                sys.stderr.write('{}\n'.format(f))
            else:
                sys.stderr.write('{} -> {}\n'.format(f, self.files[f]))
                if not self.noop: os.rename(f, files[f])



def main():
    parser = argparse.ArgumentParser(description='Given a source and destination regular expression, merge the two files into one.  Assume the file has a format of REGEX-INT.EXT.')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode.')
    parser.add_argument('--noop', action='store_true', default=False, help='Do not take any action.  Only echo.')
    parser.add_argument('--prepend', action='store_true', default=False, help='Prepend files found to the beginning.')
    parser.add_argument('nameformat', type=str, nargs='?', action='store', default=None, help='File name without numeral or extension.')
    parser.add_argument('src', type=str, nargs='*', action='store', default=None, help='Source files.')
    args = parser.parse_args()
    if not args.nameformat:
        print 'You must specify a format for the files.'
        sys.exit(1)
    if not args.src:
        print 'You must specify a list of files with which to work.'
        sys.exit(1)
    s = NumberPics(debug=args.debug, noop=args.noop, prepend=args.prepend, nameformat=args.nameformat)
    s.build_list(filelist=args.src)
    # Begin renaming files from the last and working our way toward the first.
    if args.prepend:
        last_index = s.replace_files(files=s.filenames_already_matching, index=s.total_files, digits=s.num_digits)
    else:
        last_index = s.total_files
    last_index = s.replace_files(files=s.filenames_to_change, replace_with=s.nameformat, index=last_index, digits=s.num_digits)
    last_index = s.replace_files(files=s.filenames_already_matching, index=last_index, digits=s.num_digits)
    s.update_files(files=s.files)

if __name__ == "__main__":
    main()
