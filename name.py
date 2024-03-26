#!/usr/bin/env python3
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/name.py
#=============================================================================#


import subprocess
import re
class EXIFDATA(object):
    def __init__(self, filename=None):
       self.exiftool_binary = '/usr/local/bin/exiftool'
       self.filename        = filename
       self.output          = None
       self.filedata        = {}
    def run(self):
        try:
            result = subprocess.run([self.exiftool_binary, self.filename],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            if result.returncode == 0:
                self.output = result.stdout.splitlines()
            else:
                self.output = 'ERROR: ' . str(result.stderr)
        except Exception as e:
            print('ERROR: ', str(e))
        return
    def process_output(self):
        for l in self.output:
            result = re.split(r':', l.strip(), 1)
            self.filedata[result[0].strip()] = result[1].strip()
        return
    def print_data(self):
        for i in self.filedata.keys():
            print('{:>40s}  {:<s}'.format(str(i), str(self.filedata[i])))
    def date_name(self):
        ymd = re.compile(r'^(\d\d\d\d):(\d\d):(\d\d)\s\d+.*')
        date_to_parse = None
        name = None
        # Arbitrary EXIF value for .mov files.
        if 'Track Create Date' in self.filedata.keys():
            # Creation Date -> 2016:11:28 13:02:40-08:00
            date_to_parse = self.filedata['Creation Date']
        elif 'Date/Time Created' in self.filedata.keys():
            # Date/Time Created  -> 2016:12:23 11:48:06-08:00
            date_to_parse = self.filedata['Date/Time Created']
        nums = re.match(ymd, date_to_parse)
        name = '{:04}-{:02}-{:02}'.format(nums.group(1), nums.group(2), nums.group(3))
        return name

import os
class FileNames(object):
    def __init__(self, names=None):
        self.names_orig        = {}
        self.names_new         = {}
        self.filecount         = len(names)
        for f in names:
            file_match = re.match(r'^(.*)\.([A-Za-z0-9]{3,4})\Z', f)
            (file_base,file_ext) = (file_match.group(1), file_match.group(2))
            self.names_orig[f] = { 'base'     : file_base,
                                   'ext'      : file_ext,
                                   'full'     : f }
            self.new_bases = {}
            self.names_new[f]  = {  'base'     : file_base,
                                    'ext'      : file_ext,
                                    'full'     : f }
    def clean_comment(self, comment):
        if comment is None:
            return None
        n = comment.lower()
        # Control characters (+ ? . * ^ $ ( ) [ ] { } | \)
        n = re.sub(r'&', 'and', n)
        n = re.sub(r'\s+\-\s+', '-', n)
        n = re.sub(r'\s+', '-', n)
        n = re.sub(r'\s', '-', n)
        n = re.sub(r'[^A-Za-z0-9_\.\-]', '', n)
        n = re.sub(r'-{2,}', '-', n)
        n = re.sub(r'-([^A-Za-z0-9])', r'\1', n)
        return n
    def add_numbers(self):
        for base in self.new_bases.keys():
            basecount = int(len(self.new_bases[base]))
            if basecount > 1:
                digits = len(str(basecount))
                n = int(1)
                for origname in self.new_bases[base]:
                    numbered_base = '{}-{}'.format(base, str(n).zfill(digits))
                    self.names_new[origname]['base'] = numbered_base
                    n += 1
    def build_final_names(self):
        for f in self.names_orig.keys():
            self.names_new[f]['full'] = '{newbase}.{ext}'.format(newbase=self.names_new[f]['base'],
                                                                 ext=self.names_orig[f]['ext'])
        return
    def rename_files(self, noop=False):
        for f in self.names_orig.keys():
            if os.path.isfile(self.names_new[f]['full']):
                raise Exception('File exists! {}'.format(self.names_new[f]['full']))
            print('{} --> {}'.format(f, self.names_new[f]['full']))
            if noop is False: os.rename(f, self.names_new[f]['full'])


import argparse
def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--noop', action='store_true', default=False, help='Do not take any action.  Only echo.')
    parser.add_argument('comment', action='store', type=str, default=None, help='Comments.')
    parser.add_argument('filenames', action='store', nargs='+', type=str, default=None, help='Filename')
    args = parser.parse_args()
    fn = FileNames(names=args.filenames)
    for f in fn.names_orig.keys():
        exif = EXIFDATA(f)
        exif.run()
        exif.process_output()
        filecomment = fn.clean_comment(args.comment)
        filedate = exif.date_name()
        newbase = '{}-{}'.format(filedate, filecomment)
        fn.names_new[f]['base'] = newbase
        if newbase in fn.new_bases:
            fn.new_bases[newbase].append(f)
        else:
            fn.new_bases[newbase] = [ f ]
    fn.add_numbers()
    fn.build_final_names()
    fn.rename_files(noop=args.noop)

if __name__ == "__main__":
    main()

