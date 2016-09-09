"""
This scripts evaluates top-k found from index on article and section level.
"""

import os
import sys
from optparse import OptionParser
import cPickle as pickle

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')

from es.query import QuestionQuery, QuestionQueryBuilder


def evaluate(filename, top_k=5):
    content = pickle.load(open(filename))

    print 'File used to evaluate: %s' % filename
    print 'Top \'%d\' of hits used in evaluation' % top_k

    articles_found = 0
    sections_found = 0

    for r in content:
        q_article_found = False
        q_section_found = False
        for k in r['hits'][:top_k]:
            if r['question_entity']['article'] == k['article']:
                q_article_found = True
                if r['question_entity']['section'] == k['section']:
                    q_section_found = True

        if q_article_found:
            articles_found += 1

        if q_section_found:
            sections_found += 1

    print 'Articles matched: %d (%.2f)' % (articles_found, articles_found/float(len(content))*100)
    print 'Sections matched: %d (%.2f)' % (sections_found, sections_found/float(len(content))*100)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-i', '--input',
                      action='store',
                      dest='topk_file',
                      default=None,
                      help="File with top-k results")
    (options, args) = parser.parse_args()

    if not options.topk_file:
        raise ValueError('Pass \'-i\' option')

    evaluate(options.topk_file)
