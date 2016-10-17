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

and extracts it to the json structure: articles, sections, paragraphs etc.
It omits internal Wikipedia articles, sections, discussions etc. ('Wikipedia:', 'User:' etc.)
It requires that the paragraph the number of tokens in paragraph must be larger than predefined threshold.

"""

# !/usr/bin/python
# -*- coding: utf-8 -*-

import fnmatch
import os
import sys
import json
from optparse import OptionParser
from xml_reader import XMLReader

reload(sys)
sys.setdefaultencoding('utf-8')

FILE_SUFFIX = '*[0-9][0-9]'
ARTICLE_SKIP_PREFIXES = ('User:', 'Wikipedia:', 'File:', 'MediaWiki:', 'Template:', 'Help:', 'Category:', 'Portal:',
                         'Book:', 'Draft:', 'Education Program:', 'TimedText:', 'Module:', 'Topic:', 'Gadget:',
                         'Gadget definition:')
PARAGRAPH_MIN_LENGTH = 10


def process(directory, suffix):
    files = get_xml_files(directory, suffix)
    xml_reader = XMLReader()

    all_files = len(files)
    articles_all = 0
    articles_output = 0
    paragraphs_all = 0
    paragraphs_output = 0
    iteration = 0

    for i, f in enumerate(files):
        articles_from_f = xml_reader.extract(f)
        filtered_articles = []

        articles_all += len(articles_from_f)

        for article in articles_from_f:
            if article['article'].startswith(ARTICLE_SKIP_PREFIXES):
                continue

            filtered_article = dict()
            filtered_article['article'] = article['article']
            filtered_article['id'] = article['id']
            filtered_article['url'] = article['url']
            filtered_article['sections'] = []

            for section in article['sections']:
                filtered_section = dict()
                filtered_section['section'] = section['name']
                filtered_section['paragraphs'] = []

                for paragraph in section['paragraphs']:
                    paragraphs_all += 1
                    if len(paragraph.split(' ')) >= PARAGRAPH_MIN_LENGTH:
                        filtered_section['paragraphs'].append(paragraph)

                if len(filtered_section['paragraphs']) > 0:
                    paragraphs_output += len(filtered_section['paragraphs'])
                    filtered_article['sections'].append(filtered_section)

            if len(filtered_article['sections']) > 0:
                filtered_articles.append(filtered_article)

        json.dump(filtered_articles, open(f + '.json', 'w'), indent=2)
        sys.stdout.write("\rFiles parsed: %d/%s" % (i, all_files))
        sys.stdout.flush()
        articles_output += len(filtered_articles)
        iteration += 1
    sys.stdout.write("\rFiles parmsed: %d/%d" % (iteration, all_files))
    sys.stdout.write('\n')
    sys.stdout.flush()

    print ('\nAll articles: %d\nArticles dumped to json: %d' % (articles_all, articles_output))
    print ('\nAll paragraphs: %d\nParagraphs dumped to json: %d' % (paragraphs_all, paragraphs_output))


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

    process(options.directory, FILE_SUFFIX)
