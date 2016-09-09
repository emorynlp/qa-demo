"""
This script make a count of articles that start with given prefix and/or suffix
"""

import os
import sys
from optparse import OptionParser
import fnmatch
import pickle


def search(directory, prefix, suffix):
    matched_files = []
    for root, dir_names, file_names in os.walk(directory):
        for filename in fnmatch.filter(file_names, '*.pickle'):
            matched_files.append(os.path.join(root, filename))

    counted = 0
    iteration = 0
    all_files = len(matched_files)

    for p in matched_files:
        pickle_list = pickle.load(open(p))
        for article in pickle_list:
            match = True
            if prefix and not article['article'].startswith(prefix):
                match = False
            if suffix and not article['article'].endswith(suffix):
                match = False

            if match:
                counted += 1

        iteration += 1
        sys.stdout.write("\rFiles parsed: %d/%s" % (iteration, all_files))
        sys.stdout.flush()
    sys.stdout.write("\rFiles parsed: %d/%d" % (iteration, all_files))
    sys.stdout.write('\n')
    sys.stdout.flush()

    print ('counted articles: %d' % counted)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-d', '--directory',
                      action='store',
                      dest='directory',
                      default=None,
                      help="Directory with pickle files")
    parser.add_option('-p', '--prefix',
                      action='store',
                      dest='prefix',
                      default=None,
                      help="Prefix for an article name")
    parser.add_option('-s', '--suffix',
                      action='store',
                      dest='suffix',
                      default=None,
                      help="Suffix for an article name")

    (options, args) = parser.parse_args()
    if not options.directory:
        raise ValueError('Pass \'-d\' option')

    search(options.directory, options.prefix, options.suffix)