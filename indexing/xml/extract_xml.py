"""
This script takes a structure of files with XML:

-------------------
<doc>
<section_name></section_name>
<section_name></section_name>
...
<section_name></section_name>

</doc>
<doc>
...
</doc>
...
-------------------

and extracts it to the json structure: (articles)

{

"""

import fnmatch
import os
import sys
from pprint import pprint
import cPickle as pickle
from optparse import OptionParser
from xml_reader import XMLReader

FILE_SUFFIX = '*[0-9][0-9]'
MERGE_SUFFIX = ['.tok']
MERGE_KEYS = ['tokenized']


def process(directory, suffix):
    print suffix
    files = get_xml_files(directory, suffix)
    xml_reader = XMLReader()

    all_files = len(files)
    iteration = 0

    for i, f in enumerate(files):
        extracted_f = xml_reader.extract(f)

        for m_suffix, m_key in zip(MERGE_SUFFIX, MERGE_KEYS):
            add_pickle = xml_reader.extract(f + m_suffix)

            assert len(extracted_f) == len(add_pickle), 'for file %s, %s merge suffix file has different length' % \
                                                        (f, m_suffix)

            for original, additional in zip(extracted_f, add_pickle):
                assert len(original['sections']) == len(additional['sections'])
                for o_section, a_section in zip(original['sections'], additional['sections']):
                    assert len(o_section['paragraphs']) == len(a_section['paragraphs']), '%d != %d in file %s' % \
                                                                                         (len(o_section['paragraphs']),
                                                                                          len(a_section['paragraphs']),
                                                                                          f)
                    # if len(o_section['paragraphs']) != len(a_section['paragraphs']):
                    #     pprint(o_section['paragraphs'])
                    #     pprint(a_section['paragraphs'])
                    #     raise Exception
                    o_section['paragraphs_' + m_key] = a_section['paragraphs']

        pickle.dump(extracted_f, open(f + '.pickle', 'wb'))
        iteration += 1
        sys.stdout.write("\rFiles parsed: %d/%s" % (i, all_files))
        sys.stdout.flush()
    sys.stdout.write("\rFiles parsed: %d/%d" % (iteration, all_files))
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_xml_files(directory, suffix):
    matches = []

    for root, dir_names, file_names in os.walk(directory):
        if suffix:
            for filename in fnmatch.filter(file_names, suffix):
                matches.append(os.path.join(root, filename))
        else:
            for filename in file_names:
                matches.append(os.path.join(root, filename))

    return matches

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-d', '--directory',
                      action='store',
                      dest='directory',
                      default=None,
                      help="Directory with XML files")
    parser.add_option('-s', '--suffix',
                      action='store',
                      dest='file_suffix',
                      default=None,
                      help="Suffix of files that will be considered in `directory'")
    (options, args) = parser.parse_args()

    if not options.directory:
        raise ValueError('Pass \'-d\' option')

    process(options.directory, options.file_suffix if options.file_suffix else FILE_SUFFIX)

    # process(directory)