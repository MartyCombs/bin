#!/usr/bin/env python3
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/exif.py
#=============================================================================#

import argparse, sys, os, shlex, re
import subprocess


class Exif:
    def __init__(self, filename=None):
        self.exifdata = {}
        self.maxlength = 16
        # Build the list of EXIF data for the files given.
        checkexifdata = self.read_exif_data(filename=filename)
        if checkexifdata['error'] is not None:
            sys.stderr.write('Error in exiftool for file "{}" : {}'.format(filename, checkexifdata['error']))
        else:
            self.exifdata = checkexifdata
        # Set the buffer to the longest filename found.
        for ef in self.exifdata.keys():
            if self.maxlength < len(ef):
                self.maxlength = len(ef)
    # Return EXIF data for a file if present.  Swallow errors.
    def read_exif_data(self, filename=None):
        exifdata = {}
        error = None
        cmd = ['exiftool', filename]
        try:
            exiftool_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            lines = exiftool_output.splitlines()
            for l in lines:
                match = re.search(r'(\S+)\s+\: (.*)$', l.decode('utf8'))
                exifdata[str(match.group(1))] = str(match.group(2))
        except subprocess.CalledProcessError as e:
            error = e.output
        return { 'exifdata' : exifdata,
                 'error'    : error }
    def print_exifdata(self, filename=None):
        return
    # Not implemented.
    def write_exifdata(self, filename=None):
        #cmd='exiftool -P -overwrite_original_in_place {}'.format(kwords,filename)
        #args = shlex.split(cmd)
        #subprocess.check_output(args)
        return None
    def confirm_prompt(self, prompt=None, resp=False):
        if prompt is None:
            prompt = 'Confirm'
        if resp:
            prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
        else:
            prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        while True:
            ans = raw_input(prompt)
            if not ans:
                return resp
            if ans not in ['y', 'Y', 'n', 'N']:
                print('Please enter y or n.')
                continue
            if ans == 'y' or ans == 'Y':
                return True
            if ans == 'n' or ans == 'N':
                return False


def main():
    parser = argparse.ArgumentParser(description='Update keywords on an image or movie.')
    parser.add_argument('files', metavar='FILENAME', type=str, nargs='+', default=None, help='List of image or movie files to manipulate.')
    parser.add_argument('--debug', action='store_true', default=False, help='Reflect debug information.')
    parser.add_argument('--noop', action='store_true', default=False, help='Do not do anything.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Verbose output.')
    parser.add_argument('--keep', action='store_true', default=False, help='Keep originals from exiftool')
    parser.add_argument('-a', '--addkey', nargs='?', action='append', type=str, default=None, help='List of keywords to add to EXIF data.')
    parser.add_argument('-r', '--removekey', nargs='?', action='append', type=str, default=None, help='List of keywords to remove from EXIF data.')
    parser.add_argument('-s', '--setkey', action='store', type=str, default=None, help='List of keywords to specifically set EXIF data.')
    parser.add_argument('-c', '--confirm', action='store_true', default=False, help='Confirm writing of EXIF data.')
    args = parser.parse_args()

    kw = Exifdata(files=args.files, actions=[args.addkey, args.removekey, args.setkey])
    if len(kw.files) == 0:
        sys.stderr.write('No files to update.\n')
        sys.exit(0)
    if kw.noaction == True:
        for f in args.files:
            print('File : {}\nKeywords\n'.format(f))
            kw.print_keywords(filename=f)
    for f in kw.files:
        if args.quiet == False and kw.noaction == False:
            sys.stderr.write('File : {}\n'.format(f))
            sys.stderr.write('    BEFORE : {}\n'.format(kw.keywords[f]))
        if args.addkey:
            kw.add_keywords(filename=f, keystoadd=args.addkey)
        if args.removekey:
            kw.remove_keywords(filename=f, keystoremove=args.removekey)
        if args.setkey:
            kw.set_keywords(filename=f, keywords=args.setkey)

        # Order the keywords alphabetically before writing them.
        kw.clean_list(filename=f)
        if args.quiet == False and kw.noaction == False:
            sys.stderr.write('    AFTER  : {}\n'.format(kw.keywords[f]))
    if args.noop:
        sys.exit(0)
    if args.confirm is True:
        if kw.confirm_prompt(prompt='Write metadata?', resp=False) is False:
            sys.exit(0)
    if kw.noaction is True:
        print('{fname:{chars}s}    {kwords:<}'.format(fname='Filename', chars=kw.maxlength, kwords='Keywords'))
        print('{fname:{chars}s}    {kwords:<}'.format(fname='--------', chars=kw.maxlength, kwords='--------'))
    for f in kw.files:
        if kw.noaction is True:
            print('{fname:{chars}s}    {kwords:<}'.format(fname=f, chars=kw.maxlength, kwords=kw.keywords[f]))
        else:
            if kw.keywords[f] != kw.keywords_before[f]:
                kw.write_keywords(filename=f)


if __name__ == "__main__":
    main()
