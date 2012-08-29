#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2010, Torbjörn Lönnemark <tobbez@ryara.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import sys
import getopt
import urllib
import urllib2
import urlparse
import json
from os.path import basename


def which(program_name):
    for p in os.environ['PATH'].split(os.path.pathsep):
        abs_path = os.path.join(p, program_name)
        if os.path.exists(abs_path):
            return abs_path
    return None

def add_to_qs(url, kvs):
    u = list(urlparse.urlparse(url))
    qs = dict(urlparse.parse_qsl(u[4]))
    qs.update(kvs)
    u[4] = urllib.urlencode(qs)

    # urlparse discards params with no value - hopefully, this should not be a
    # problem

    return urlparse.urlunparse(u)


def usage():
    print "Usage: %s [-d] [-o <output>] <url>" % (sys.argv[0])
    print " -d: Download stream using rtmpdump (if available)"
    print " -o: Specifies path to download to. Implies -d."
    

def main():
    opts=None
    args=None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'do:')
    except getopt.GetoptError as e:
        sys.stderr.write('Error: ' + str(e) + '\n')
        print
        usage()
        return 1
        
    if len(args) != 1:
        usage()
        return 1

    do_download = False
    output_path = None
    for k, v in opts:
        if k == '-d':
            do_download = True
        elif k == '-o':
            do_download = True
            output_path = v

    url = add_to_qs(args[0], {'output': 'json'})

    page_contents = None
    try:
        page_contents = urllib2.urlopen(url).read()
    except Exception as e:
        sys.stderr.write('Error while fetching page: ' + str(e) + '\n')
        return 1

    j = json.loads(page_contents)
    video_links = j['video']['videoReferences']
    video_links.sort(key = lambda x: x['bitrate'], reverse=True)

    rtmp_url = video_links[0]['url']

    if do_download:
        if which('rtmpdump') != None:
            if not output_path:
                output_path = basename(rtmp_url);

            print 'Downloading to ' + output_path
            os.system('rtmpdump -r ' + rtmp_url + ' -o ' + output_path)
        else:
            sys.stderr.write('Error: rtmpdump not found, not downloading\n')
    else:
        print rtmp_url

    return 0
    
if __name__ == '__main__':
    sys.exit(main())
