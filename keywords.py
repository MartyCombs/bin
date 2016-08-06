#!/usr/bin/env python

import argparse, sys, os, shlex, re
import subprocess


class Keyword:
    'Manage keywords for files which can have them.'
    def __init__(self, files=None, actions=None):
        '''
Parameters
    files          List of files to examine and/or alter.
    actions        List of actions to take.
        '''
        self.files = []
        self.files_skipped = []
        self.keywords_before = {}
        self.keywords = {}
        self.maxlength = len('Filename')
        # If every element in the list of actions is 'None', no action should be taken.
        self.noaction = True
        if type(actions) is list:
            for a in actions:
                if type(a) is list:
                    self.noaction = False
        for f in files:
            if not os.path.exists(f):
                sys.stderr.write('File not found "{}"'.format(f))
                self.files_skipped.append(f)
                continue
            else:
                checkexifdata = self.read_exif_data(filename=f)
                if checkexifdata['error'] is not None:
                    sys.stderr.write('Error in exiftool for file "{}" : {}'.format(f, checkexifdata['error']))
                    self.files_skipped.append(f)
                else:
                    self.files.append(f)
                    self.keywords[f] = checkexifdata['keywords']
                    self.keywords_before[f] = self.keywords[f].sort()
        # Set the buffer to the longest filename found.
        for ef in self.keywords.keys():
            if self.maxlength < len(ef):
                self.maxlength = len(ef)
    def read_exif_data(self, filename=None):
        keywords = []
        error = None
        cmd = ['exiftool', '-Keywords', filename]
        try:
            exiftool_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            kwords = re.search(r'\: (.*)$', exiftool_output).group(1)
            keywords = [k.strip() for k in kwords.split(',')]
        except AttributeError:
            self.keywords[filename] = []
        except subprocess.CalledProcessError as e:
            error = e.output
        return { 'keywords' : keywords,
                 'error' : error }
    def print_keywords(self, filename):
        print '{:<}'.format(self.keywords[filename])
    def clean_list(self, filename):
        self.keywords[filename] = list(set(self.keywords[filename]))
        self.keywords[filename].sort()
    def add_keywords(self, filename, keystoadd):
        keywords_existing = self.keywords[filename]
        for keytoadd in keystoadd:
            if not keytoadd in keywords_existing:
                self.keywords[filename].append(keytoadd)
    def remove_keywords(self, filename, keystoremove):
        keywords_existing = self.keywords[filename]
        for keytoremove in keystoremove:
            if keytoremove in keywords_existing:
                self.keywords[filename].remove(keytoremove)
    def set_keywords(self, filename, keywords):
        self.keywords[filename] = keywords.split()
    def write_keywords(self, filename):
        kwords = ', '.join(self.keywords[filename])
        cmd='exiftool -overwrite_original_in_place -Keywords="{}" {}'.format(kwords,filename)
        args = shlex.split(cmd)
        subprocess.check_output(args)
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
                print 'Please enter y or n.'
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

    kw = Keyword(files=args.files, actions=[args.addkey, args.removekey, args.setkey])
    if len(kw.files) == 0:
        sys.stderr.write('No files to update.\n')
        sys.exit(0)
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
        print '{fname:{chars}s}    {kwords:<}'.format(fname='Filename', chars=kw.maxlength, kwords='Keywords')
        print '{fname:{chars}s}    {kwords:<}'.format(fname='--------', chars=kw.maxlength, kwords='--------')
    for f in kw.files:
        if kw.noaction is True:
            print '{fname:{chars}s}    {kwords:<}'.format(fname=f, chars=kw.maxlength, kwords=kw.keywords[f])
            if kw.keywords[f] != kw.keywords_before[f]:
                kw.write_keywords(filename=f)


if __name__ == "__main__":
    main()
