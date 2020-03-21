#!/usr/bin/env python3
#=============================================================================#
# https://github.com/MartyCombs/bin/blob/master/pic-number.py
#=============================================================================#

'''
Given a regular expression, adjust file names to match the regular expression.
'''
import argparse, sys, os, glob, re, tempfile, logging

class NumberPics:
    def __init__(self, debug=False, loglevel=None, noop=False, prepend=False, nameformat=None, dstdir=None, srcfiles=None):
        '''Want files of format:
    BASE-DIGITS.EXTENSION
where BASE-DIGITS are unique regardless of EXTENSION (i.e. 'name-1.jpg'
cannot equal 'name-1.png').
        '''
        self.debug = debug
        self.loglevel = loglevel.upper()
        self.noop = noop
        self.prepend = prepend
        self.nameformat = nameformat          # BASE
        self.dstdir = os.path.abspath(dstdir) # Destination directory.
        self.srcfiles = []                    # List of source files.
        for f in srcfiles:
            self.srcfiles.append(os.path.abspath(f))
        self.filename_format = re.compile(r'^(\S+)\-(\d+)\.([A-Za-z0-9]{1,4})\Z')
        self.anyfile_format = re.compile(r'^(\S+)\.([A-Za-z0-9]{1,4})\Z')
        self.ordered_files = []
        self.files = {}
        self.totalfiles = int(0)
        self.digits = int(0)
        self.list_order = [ 'matching_dst_files', 'matching_src_files', 'other_dst_files', 'other_src_files' ]
        self.match_order = [ 'matching', 'other' ]
        self.ds_order = [ 'dst', 'src' ]
        self.file_lists = { 'matching' : { 'dst' : [],
                                           'src' : [] },
                            'other'    : { 'dst' : [],
                                           'src' : [] } }
        self.init_logging(loglevel=self.loglevel)



    def init_logging(self, loglevel=None):
        '''Assumes self.loglevel = 'critical|error|warning|info|debug'
        '''
        levels = [ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG' ]
        if loglevel.upper() not in levels:
            loglevel='WARNING'
        log = logging.getLogger(__name__)
        formatter_basic = logging.Formatter(fmt='[%(asctime)s] %(levelname)8s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
        formatter_debug = logging.Formatter(fmt='DEBUG: [%(asctime)s] %(filename)s(%(process)d) %(levelname)8s [%(name)s.%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
        sh = logging.StreamHandler(stream=sys.stderr)
        if self.debug:
            loglevel='DEBUG'
            sh.setFormatter(formatter_debug)
        else:
            loglevel = loglevel.upper()
            sh.setFormatter(formatter_basic)
        log.setLevel(getattr(logging, loglevel))
        log.addHandler(sh)
        self.log = log



    def remove_dupes(self, filelist=None):
        endlist = []
        filecheck = {}
        for f in filelist:
            fullname = os.path.abspath(f)
            if fullname in filecheck:
                continue
            else:
                filecheck[fullname] = 1
                endlist.append(fullname)
        return endlist



    def get_file_parts(self, filename):
        '''Break a file into the three parts we want:
    dir   : base directory
    base  : base file name
    n     : file number matching 'base' (Can be None).
    ext   : file extension after the period
        '''
        full_filename = os.path.abspath(filename)
        f = { 'dir' : None, 'base' : None, 'n' : None, 'ext' : None }
        if not os.path.isfile(full_filename):
            self.log.debug('Not a file "{}"'.format(full_filename))
            return f
        f['dir'] = os.path.dirname(full_filename)
        match_format = re.match(self.filename_format, os.path.basename(full_filename))
        match_any = re.match(self.anyfile_format, os.path.basename(full_filename))
        if match_format:
            (f['base'], f['n'], f['ext']) = (match_format.group(1), match_format.group(2), match_format.group(3))
        elif match_any:
            (f['base'], f['ext']) = (match_any.group(1), match_any.group(2))
        else:
            self.log.debug('File "{}" matched neither format nor any file type.'.format(full_filename))
        return  f



    def get_file_lists(self, file_list=None, nameformat=None):
        files = { 'matching' : [],
                  'other' : [] }
        for f in file_list:
            parts = self.get_file_parts(filename=f)
            fullname = None
            if parts['dir'] == None or parts['base'] == None or parts['ext'] == None:
                self.log.debug('Skipping file "{}".'.format(os.path.basename(f)))
                continue
            if parts['base'] == nameformat:
                if parts['n'] != None:
                    fullname = parts['dir'] + '/' + parts['base'] + '-' + parts['n'] + '.' + parts['ext']
                else:
                    fullname = parts['dir'] + '/' + parts['base'] + '.' + parts['ext']
                files['matching'].append(fullname)
            else:
                if parts['n'] != None:
                    fullname = parts['dir'] + '/' + parts['base'] + '-' + parts['n'] + '.' + parts['ext']
                else:
                    fullname = parts['dir'] + '/' + parts['base'] + '.' + parts['ext']
                files['other'].append(fullname)
        return files



    def check_if_dst_dir_in_src_files(self, destdir=None, srcfiles=None):
        for f in srcfiles:
            parts = self.get_file_parts(filename=f)
            if parts['dir'] == destdir:
                self.log.debug('Found destination directory in the list of source files "{}"'.format(parts['dir']))
                self.ds_order.remove('dst')
                return
        return



    def build_names(self):
        self.totalfiles = int(len(self.files.keys()))
        if self.debug:
            self.log.debug('Detected {} total files.'.format(self.totalfiles))
        self.digits = int(len(str(self.totalfiles)))
        n = int(1)
        for f in self.ordered_files:
            parts = self.get_file_parts(f)
            newname = os.path.abspath(self.dstdir) + '/' + self.nameformat + '-' + str(n).zfill(self.digits) + '.' + parts['ext'].lower()
            self.files[f] = newname
            n = n + 1
        return



    def update_files(self):
        '''
        '''
        for f in self.ordered_files:
            if f == self.files[f]:
                if self.debug == True :
                    sys.stderr.write('{}\n'.format(os.path.basename(self.files[f])))
            else:
                sys.stderr.write('{} -> {}\n'.format(os.path.basename(f), os.path.basename(self.files[f])))
                if not self.noop:
                    if f == self.files[f]:
                        sys.stderr.write('WARNING: Source and target are the same. "{}" == "{}" \n'.format(f, self.files[f]))
                    else:
                        os.rename(f, self.files[f])



def main():
    parser = argparse.ArgumentParser(description='Given a source and destination regular expression, merge the two files into one.  Assume the file has a format of REGEX-INT.EXT.')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode.')
    parser.add_argument('--loglevel', action='store', default='WARNING', help='Set a specific log level.')
    parser.add_argument('--noop', action='store_true', default=False, help='Do not take any action.  Only echo.')
    parser.add_argument('--prepend', action='store_true', default=False, help='Prepend files found to the beginning.')
    parser.add_argument('nameformat', type=str, nargs='?', action='store', default=None, help='File name without numeral or extension.')
    parser.add_argument('dstdir', type=str, nargs='?', action='store', default=None, help='Destination directory.')
    parser.add_argument('srcfiles', type=str, nargs='*', action='store', default=None, help='Source files.')
    args = parser.parse_args()
    if not args.nameformat:
        print('You must specify a format for the files.')
        sys.exit(1)
    if not args.srcfiles:
        print('You must specify a list of files with which to work.')
        sys.exit(1)
    if not args.dstdir:
        raise AttributeError('Destination directory not defined.')
        sys.exit(1)
    if not os.path.exists(args.dstdir) or not os.path.isdir(args.dstdir):
        raise IOError('Destination directory "{}" does not exist or is not a directory'.format(args.dstdir))
        sys.exit(1)

    s = NumberPics(debug=args.debug, loglevel=args.loglevel, noop=args.noop, prepend=args.prepend, nameformat=args.nameformat, dstdir=args.dstdir, srcfiles=args.srcfiles)
    s.srcfiles = s.remove_dupes(filelist=s.srcfiles)
    '''First build the source and destination lists which we use.  Lists in order of preference
          1. ['matching'] ['dst'] Files in destination directory matching pattern
          2. ['matching'] ['src'] Files in source list matching pattern
          3. ['other']    ['dst'] Other files in destination directory
          4. ['other']    ['src'] Other source files
    with a specific exclusion where #1 and #2 are skipped if the destination directory is
    included in the source list.
    '''
    dstdirfiles = []
    for node in sorted(os.listdir(s.dstdir), reverse=False):
        if node.startswith('.'):
            next
        dstdirfiles.append(os.path.abspath(s.dstdir) + '/' + node)
    dstdirlists = s.get_file_lists(file_list=sorted(dstdirfiles), nameformat=s.nameformat)
    s.file_lists['matching']['dst'] = dstdirlists['matching']
    ''' Leave ['other']['dst'] null as the destination directory
        might have differently labelled files than what we want to label -
        i.e. if we are numbering files
           ./testdir/IMG_1234.jpg       --> ./General/SF-Bob-1.jpg,

        we do not want to accidentally number files

           ./General/SF-General-1.jpg   --> ./General/SF-Bob-2.jpg
    '''
    s.file_lists['other']['dst'] = []

    srcfilelists = s.get_file_lists(file_list=s.srcfiles, nameformat=s.nameformat)
    s.file_lists['matching']['src'] = srcfilelists['matching']
    s.file_lists['other']['src'] = srcfilelists['other']

    s.check_if_dst_dir_in_src_files(destdir=s.dstdir, srcfiles=s.srcfiles)
    if args.prepend:
        for mo in reversed(s.match_order):
            for so in s.ds_order:
                for f in s.file_lists[mo][so]:
                    s.ordered_files.append(f)
                    s.files[f] = None
    else:
        for mo in s.match_order:
            for so in s.ds_order:
                for f in s.file_lists[mo][so]:
                    s.ordered_files.append(f)
                    s.files[f] = None
    s.build_names()
    s.update_files()


if __name__ == "__main__":
    main()

