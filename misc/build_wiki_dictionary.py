"""
This script takes a set of Wikipedia pickle files and prepares a map of:

{
  article_id: {'name': <name>,
               'url': <url>},
"""

import os
import sys
from optparse import OptionParser
import json
import fnmatch
import cPickle as pickle
from elasticsearch import Elasticsearch
from collections import Counter

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')

from es.query import QueryPreprocessor


def process(directory, output_file):
    matched_files = []
    for root, dir_names, file_names in os.walk(directory):
        for filename in fnmatch.filter(file_names, '*.pickle'):
            matched_files.append(os.path.join(root, filename))

    iteration = 0
    all_files = len(matched_files)
    di = dict()

    for p in matched_files:
        qs = pickle.load(open(p))
        for q in qs:
            di_item = {'url': q['url'], 'name': q['article'], 'pickle': p}
            di[q['id']] = di_item

        iteration += 1
        sys.stdout.write("\rFiles parsed: %d/%s" % (iteration, all_files))
        sys.stdout.flush()
    sys.stdout.write("\rFiles parsed: %d/%d" % (iteration, all_files))
    sys.stdout.write('\n')
    sys.stdout.flush()

    print 'About to dump pickle with %d keys' % len(di.keys())
    pickle.dump(di, open(output_file, 'wb'))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-d', '--directory',
                      action='store',
                      dest='directory',
                      default=None,
                      help="Directory with pickle files")
    parser.add_option('-o', '--output',
                      action='store',
                      dest='output_file',
                      default=None,
                      help="Dictionary output file")
    (options, args) = parser.parse_args()

    if not options.directory or not options.output_file:
        raise ValueError('Pass \'-d\' and \'-o\' options')

    process(options.directory, options.output_file)
