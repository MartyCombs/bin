#!/usr/bin/env python2.7
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-number.py
#=============================================================================#

'''
Given a regular expression, adjust file names to match the regular expression.
'''
import argparse, sys, os, glob, re, tempfile

class NumberPics:
    def __init__(self, debug=False, noop=False, prepend=False, nameformat=None):
        '''Want files of format:
    BASE-DIGITS.EXTENSION
where BASE- DIGITS are unique regardless of EXTENSION (i.e. name-1.jpg == name-1.png).

There are three lists:
    * Files to skip - such as files (like thumbnails) beginning with a dot '.'.
    * Files already matching the name we want.
    * Files which need to be changed to the format we want.
        '''
        self.debug = debug
        self.noop = noop
        self.prepend = prepend
        self.nameformat = nameformat
        self.filenames_skipped = []
        self.filenames_already_matching = []
        self.filenames_to_change = []
        self.filename_format = re.compile(r'^(\S+)\-(\d+)\.([A-Za-z0-9]{1,4})\Z')
        self.anyfile_format = re.compile(r'^(\S+)\.([A-Za-z0-9]{1,4})\Z')
        self.total_files = 0
        self.num_digits = 0
        self.files = {}
    def build_list(self, format_desired=None, filelist=None):
        '''Build the list of files which are candidates for renaming.
        '''
        already_matching = []
        to_skip = []
        to_change = []
        for f in sorted(filelist):
            file_path = os.path.dirname(f)
            file_base = os.path.basename(f)
            (root, digits, extension) = self.get_file_parts(filename=file_base)
            # Files beginning with a period are skipped.  They may be thumbnails.
            if file_base.startswith('.'):
                to_skip.append(f)
            elif root == self.nameformat:
                already_matching.append(f)
            else:
                to_change.append(f)
        self.filenames_already_matching = already_matching
        self.filenames_to_change = to_change
        self.filenames_skipped = to_skip
        self.total_files = len(already_matching) + len(to_change)
        self.num_digits = len(str(self.total_files))
    def get_file_parts(self, filename=None):
        '''Break a file into the three parts we want:
    * BASE - some tag
    * DIGITS - files of that tag
    * EXTENSION - everything after the last period (i.e. jpg, png)
        '''
        (basename, digits, extension) = (None, None, None)
        match_format = re.match(self.filename_format, filename)
        match_any = re.match(self.anyfile_format, filename)
        if match_format:
            (basename, digits, extension) = (match_format.group(1), match_format.group(2), match_format.group(3))
        elif match_any:
            (basename, extension) = (match_any.group(1), match_any.group(2))
        return  (basename, digits, extension)
    def replace_files(self, files=None, replace_with=None, index=None, digits=0):
        '''
        '''
        if index < 1: return index
        rename = {}
        for f in sorted(files, reverse=True):
            file_path = os.path.dirname(f)
            if len(file_path) > 0: file_path = file_path + '/'
            file_base = os.path.basename(f)
            (file_root, file_digits, file_extension) = self.get_file_parts(filename=file_base)
            oldname = f
            if replace_with:
                replace = re.match(self.anyfile_format, file_base)
                newname = file_path + replace_with + '-' + str(index).zfill(digits) + '.' + replace.group(2).lower()
            else:
                if file_root == self.nameformat:
                    replace_digits = re.match(self.filename_format, file_base)
                    newname = file_path + replace_digits.group(1) + '-' + str(index).zfill(digits) + '.' + replace_digits.group(3).lower()
                else:
                    keep = re.match(self.anyfile_format, file_base)
                    newname = file_path + keep.group(1) + '-' + str(index).zfill(digits) + '.' + keep.group(2).lower()
            self.files[newname] = oldname
            index -= 1
        return index
    def update_files(self, files=None):
        '''Remember that the dictionary is [newname] : oldname
        '''
        for f in sorted(files, reverse=True):
            base_src = re.match(self.anyfile_format, self.files[f]).group(1)
            base_dst = re.match(self.anyfile_format, f).group(1)
            dest_exists = glob.glob(base_dst + '.*')
            if base_src == base_dst:
                sys.stderr.write('{}\n'.format(self.files[f]))
            else:
                sys.stderr.write('{} -> {}\n'.format(self.files[f], f))
                if not self.noop:
                    if base_src == base_dst:
                        sys.stderr.write('WARNING: File already exists "{}". Cannot rename "{}" ->X "{}" \n'.format(dest_exists, f, item[f]))
                    else:
                        os.rename(self.files[f], f)
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
    s.build_list(format_desired=args.nameformat, filelist=args.src)
    '''
    Order of s.files[] is important!!!!!

    Rename files from last to first.  This should prevent overwriting a pre-existing file.
    However we can choose to prepend files files to the beginning of the list.  In that case begin
    with the files already matching the name we want.
    '''
    if args.prepend:
        last_index = s.replace_files(files=s.filenames_already_matching, index=s.total_files, digits=s.num_digits)
    else:
        last_index = s.total_files
    last_index = s.replace_files(files=s.filenames_to_change, replace_with=s.nameformat, index=last_index, digits=s.num_digits)
    last_index = s.replace_files(files=s.filenames_already_matching, index=last_index, digits=s.num_digits)
    s.update_files(files=s.files)

if __name__ == "__main__":
    main()
