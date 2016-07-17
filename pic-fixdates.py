#!/usr/bin/env python

import argparse, sys, os, subprocess, shlex, re

def main():
    parser = argparse.ArgumentParser(description='Update keywords on an image or movie.')
    parser.add_argument('--gps-src', metavar='FILENAME', type=str, nargs='?', help='File to source for GPS coordinates.')
    parser.add_argument('--gps', metavar='FILENAME', type=str, nargs='?', help='GPS coordinates.')
    parser.add_argument('--dt', metavar='FILENAME', type=int, nargs='?', help='Date adjustment (seconds).')
    parser.add_argument('files', metavar='FILENAME', type=str, nargs='+', help='List of image or movie files to manipulate.')
    args = parser.parse_args()
    s = ExifData()
    s.read_exif(files=args.files)
    s.fix_keys()
    s.build_commands()
    s.execute_commands()



class ExifData(object):
    exifdata={}
    def __init__(self):
        self.exifdata_orig = {}
        self.exifdata_new = {}
        self.exifdates = ['Modify Date', 'Date/Time Original', 'Create Date']
        self.cmds = []
    def read_exif(self, files=None):
        spaces = re.compile(r'\s')
        datapairs = re.compile(r'^(.*)\s+: (.*)$')
        for f in files:
            p = subprocess.Popen(['exiftool', f], stdout=subprocess.PIPE)
            while True:
                o = p.stdout.readline().rstrip()
                if o == '' and p.poll() != None: break
                if datapairs.match(o):
                    items = datapairs.match(o).group(0).split(' : ')
                    #self.exifdata_orig[re.sub(spaces, '', items[0])] = items[1]
                    (key, value) = (items[0].rstrip(), items[1])
                    if key in self.exifdates:
                        self.exifdata_orig[f] = self.exifdata_orig.get(f, {})
                        self.exifdata_orig[f][key] = value
    def fix_keys(self):
        regex_dt = re.compile(r'^(\d+:\d\d:\d\d) (\d\d)(:\d\d:\d\d)$')
        regex_clean = re.compile(r'[\s\/]')
        for f in self.exifdata_orig.keys():
            for k in self.exifdata_orig[f].keys():
                k_new = re.sub(regex_clean, '', k)
                matches = regex_dt.search(self.exifdata_orig[f][k])
                (ymd, hr, tm) = matches.group(1,2,3)
                newhr = '{0} {1:02d}{2}'.format(ymd, (int(hr) + 4), tm)
                self.exifdata_new[f] = self.exifdata_new.get(f, {})
                self.exifdata_new[f][k_new] = newhr
    def build_commands(self):
        for f in self.exifdata_new.keys():
            cmd = 'exiftool'
            for k in self.exifdata_new[f].keys():
                cmd += ' -{}="{}"'.format(k, self.exifdata_new[f][k])
            cmd += ' {}'.format(f)
            self.cmds.append(cmd)
    def execute_commands(self):
        for cmd in self.cmds:
            print 'Executing : {}'.format(cmd)
            args = shlex.split(cmd)
            subprocess.check_output(args)


if __name__ == '__main__':  main()
