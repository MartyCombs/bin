#!/usr/bin/env python2.7

import argparse, sys, os, fnmatch, re, tempfile

class PicMerge:
    def __init__(self, debug=False, noop=False, prepend=False, directory=None, src=None, dst=None):
        self.debug = debug
        self.noop = noop
        self.prepend = prepend
        self.directory = directory
        self.src = src
        self.dst = dst
        self.filenames_src = []
        self.filenames_dst = []
        self.files = {}
        self.tmpdir = tempfile.mkdtemp()
    def replace_files(self, files=None, replace_with=None, index=None):
        if index < 1: return index
        for f in sorted(files, reverse=True):
            if replace_with:
                newname = re.sub(r'(\A.*)\-\d+\.([A-Za-z0-9]{3,4})\Z', replace_with + str(index) + r'.\2', f)
            else:
                newname = re.sub(r'(\A.*)\-\d+\.([A-Za-z0-9]{3,4})\Z', r'\1-' + str(index) + r'.\2', f)
            self.files[f] = newname
            index -= 1
        return index
def main():
    parser = argparse.ArgumentParser(description='Given a source and destination regular expression, merge the two files into one.  Assume the file has a format of REGEX-INT.EXT.')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode.')
    parser.add_argument('--noop', action='store_true', default=False, help='Do not take any action.  Only echo.')
    parser.add_argument('--prepend', action='store_true', default=False, help='Prepend files found to the beginning.')
    parser.add_argument('-d', '--dir', type=str, nargs='?', action='store', default=os.getcwd(), help='Directory in which to work.')
    parser.add_argument('src', type=str, nargs='?', action='store', default=None, help='Source regex.')
    parser.add_argument('dst', type=str, nargs='?', action='store', default=None, help='Destination filename.')
    args = parser.parse_args()
    if not args.src:
        print 'You must specify a source expression'
        sys.exit(1)
    if not args.dst:
        print 'You must specify a destination expression'
        sys.exit(1)
    s = PicMerge(prepend=args.prepend, directory=args.dir, src=args.src, dst=args.dst)
    for f in os.listdir(args.dir):
        # Skip any files which begin with a dot as they may be thumbnails.
        if f.startswith('.'): continue
        if fnmatch.fnmatch(f, '*' + args.src + '*'):
            s.filenames_src.append(f)
        elif fnmatch.fnmatch(f, '*' + args.dst + '*'):
            s.filenames_dst.append(f)
    if args.prepend:
        i = s.replace_files(files=s.filenames_dst, index=len(s.filenames_src) + len(s.filenames_dst))
    else:
        i = len(s.filenames_src) + len(s.filenames_dst)
    i = s.replace_files(files=s.filenames_src, replace_with=args.dst + '-', index=i)
    i = s.replace_files(files=s.filenames_dst, index=i)
    '''
    i = len(s.filenames_src) + len(s.filenames_dst)
    for f in sorted(s.filenames_dst, reverse=True):
        newname = re.sub(r'(\A.*)\-\d+\D*\.([A-Za-z0-9]{3,4})\Z', r'\1-' + str(i) + r'.\2', f)
        s.files[f] = newname
        i -= 1
    for f in sorted(s.filenames_src, reverse=True):
        newname = re.sub(r'(\A.*)\-\d+\D*\.([A-Za-z0-9]{3,4})\Z', args.dst + str(i) + r'.\2', f)
        s.files[f] = newname
        i -= 1
    '''
    if args.debug: print 'Creating temp directory {}'.format(s.tmpdir)
    for f in sorted(s.files.keys()):
        if f == s.files[f]:
            print '{}'.format(f)
        else:
            print '{} -> {}'.format(f, s.files[f])
            if not args.noop:
                os.rename(f, s.tmpdir + '/' + s.files[f])
    if not args.noop:
        for f in os.listdir(s.tmpdir):
            os.rename(s.tmpdir + '/' + f, f)
        os.rmdir(s.tmpdir)

if __name__ == "__main__":
    main()
