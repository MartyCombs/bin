#!/usr/bin/env python

import argparse, sys, os, subprocess, shlex, re

parser = argparse.ArgumentParser(description='Update keywords on an image or movie.')
parser.add_argument('files', metavar='FILENAME', type=str, nargs='+', help='List of image or movie files to manipulate.')
parser.add_argument('--debug', action='store_true', help='Reflect debug information.')
parser.add_argument('--keep', action='store_true', help='Keep originals from exiftool')
parser.add_argument('-a', '--addkey', nargs='?', action='append', type=str, help='List of keywords to add to EXIF data.')
parser.add_argument('-r', '--removekey', nargs='?', action='append', type=str, help='List of keywords to remove from EXIF data.')
parser.add_argument('-s', '--setkey', action='store', type=str, help='List of keywords to specifically set EXIF data.')
parser.add_argument('-c', '--confirm', action='store_true', help='Confirm writing of EXIF data.')
args = parser.parse_args()

#-----------------------------------------------------------------------------#
# Sanity tests
filenames=[]
files_skipped=[]
for filename in args.files:
    if not os.path.exists(filename):
        files_skipped.append(filename)
    else:
        checkexifdata = subprocess.check_output(["exiftool", "-Keywords", filename])
        if checkexifdata is None:
            files_skipped.append(filename)
        else:
            filenames.append(filename)

class Keyword:
    'Add keywords to an image file'
    exifdata={}
    def __init__(self, filelist):
        self.files = filelist
    def ReadExif(self):
        for filename in self.files:
            try:
                exiftool_output = subprocess.check_output(["exiftool", "-Keywords", filename])
                kwords = re.search(r'\: (.*)$', exiftool_output).group(1)
                Keyword.exifdata[filename] = [k.strip() for k in kwords.split(',')]
            except AttributeError:
                Keyword.exifdata[filename] = []
    def PrintKeywords(self, imagefile):
        print 'File {}'.format(imagefile)
        print '     {}'.format(Keyword.exifdata[imagefile])
    def CleanList(self, imagefile):
        Keyword.exifdata[imagefile] = list(set(Keyword.exifdata[imagefile]))
        Keyword.exifdata[imagefile].sort()
    def AddKeywords(self, imagefile, keystoadd):
        keywords_existing = Keyword.exifdata[imagefile]
        for keytoadd in keystoadd:
            if not keytoadd in keywords_existing:
                Keyword.exifdata[imagefile].append(keytoadd)
    def RemoveKeywords(self, imagefile, keystoremove):
        keywords_existing = Keyword.exifdata[imagefile]
        for keytoremove in keystoremove:
            if keytoremove in keywords_existing:
                Keyword.exifdata[imagefile].remove(keytoremove)
    def SetKeywords(self, imagefile, keywords):
        Keyword.exifdata[imagefile] = keywords.split()
    def WriteKeywords(self, imagefile):
        kwords = ', '.join(Keyword.exifdata[imagefile])
        cmd='exiftool -Keywords="{}" {}'.format(kwords,imagefile)
        args = shlex.split(cmd)
        subprocess.check_output(args)
    def ConfirmPrompt(self, prompt=None, resp=False):
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


#-----------------------------------------------------------------------------#
kw = Keyword(filenames)
kw.ReadExif()
for filename in filenames:
    if kw.debug:
        print 'File : {}'.format(filename)
        print '    BEFORE : {}'.format(kw.exifdata[filename])
    if args.addkey:
        kw.AddKeywords(imagefile = filename, keystoadd = args.addkey)
    if args.removekey:
        kw.RemoveKeywords(imagefile = filename, keystoremove = args.removekey)
    if args.setkey:
        kw.SetKeywords(imagefile = filename, keywords = args.setkey)

    # Order the keywords alphabetically before writing them.
    kw.CleanList(imagefile = filename)
    if kw.debug:
        print '    AFTER  : {}'.format(kw.exifdata[filename])
    if args.confirm is True:
        if kw.ConfirmPrompt(prompt='Write metadata?', resp=False) is True:
            kw.WriteKeywords(filename)
    else:
        kw.WriteKeywords(filename)
