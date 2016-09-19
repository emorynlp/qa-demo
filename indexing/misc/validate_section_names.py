"""
This script loads all the pickles from given directory
and checks whether there any dashes ('-') in article or
sections names
"""

import os
import sys
from optparse import OptionParser
import fnmatch
import pickle


def validate(directory):
    matched_files = []
    for root, dir_names, file_names in os.walk(directory):
        for filename in fnmatch.filter(file_names, '*.pickle'):
            matched_files.append(os.path.join(root, filename))

    for p in matched_files:
        pickle_list = pickle.load(open(p))
        for article in pickle_list:
            if '_' in article['article']:
                print ('article %s in pickle %s has a dash' % (article['article'], p))
            for section in article['sections']:
                if '_' in section['name']:
                    print ('article %s, section %s in pickle %s has a dash' % (article['article'],
                                                                               section['name'], p))

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-d', '--directory',
                      action='store',
                      dest='directory',
                      default=None,
                      help="Directory with pickle files")

    (options, args) = parser.parse_args()
    if not options.directory:
        raise ValueError('Pass \'-d\' option')

    validate(options.directory)