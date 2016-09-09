"""
This script performs an experiment querying paragraph fields and retrieving
their sections and articles. It assumes that every question in the pickle
file comes with a correct article and section.
Then, the count for articles and section is printed and the top-k file
is stored.
"""

import os
import sys
from optparse import OptionParser
import cPickle as pickle

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')

from es.query import QuestionQuery, QuestionQueryBuilder


def experiment(filename, es_server, es_index, es_type, query_field='text', top_k=5):
    content = pickle.load(open(filename))

    print 'Using the questions from file: %s' % filename
    print 'ElasticSearch will use top \'%d\' of results' % top_k
    print 'ElasticSearch will query on the \'%s\' field' % query_field

    articles_found = 0
    sections_found = 0

    qqb = QuestionQueryBuilder()
    queries = qqb.build_query(content, [query_field])

    qq = QuestionQuery(es_server, es_index, es_type)
    res = qq.query_index(queries, top_k)

    for r in res:
        q_article_found = False
        q_section_found = False
        for k in r['hits']:
            if r['question_entity']['article'] == k['article']:
                q_article_found = True
                if r['question_entity']['section'] == k['section']:
                    q_section_found = True

        if q_article_found:
            articles_found += 1

        if q_section_found:
            sections_found += 1

    print 'Articles matched: %d (%.2f)' % (articles_found, articles_found/float(len(res))*100)
    print 'Sections matched: %d (%.2f)' % (sections_found, sections_found/float(len(res))*100)

    o_path = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
    o_file = filename.split('/')[-1].rstrip('.pickle') + '_' + es_index + '_top' + str(top_k) + '.pickle'

    print 'Dumping top_k results file to: %s' % (o_path + o_file)
    pickle.dump(res, open(o_path + o_file, 'wb'))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-q', '--questions',
                      action='store',
                      dest='questions',
                      default=None,
                      help="Filename with questions pickle")
    parser.add_option('-e', '--elasticserver',
                      action='store',
                      dest='es_server',
                      default=None,
                      help="IP of the ElasticSearch server to use")
    parser.add_option('-i', '--indexname',
                      action='store',
                      dest='es_index',
                      default=None,
                      help="Index name in the ElasticSearch server")
    parser.add_option('-t', '--typename',
                      action='store',
                      dest='es_type',
                      default=None,
                      help="Type name in the index")
    parser.add_option('--topk',
                      action='store',
                      dest='top_k',
                      default=5,
                      help='What top-results from ElasticSearch to use')
    parser.add_option('--query_field',
                      action='store',
                      dest='query_field',
                      default='text',
                      help='What field in index to query')
    (options, args) = parser.parse_args()

    if not options.questions or not options.es_server or not options.es_index:
        raise ValueError('Pass \'-q\', \'-e\', \'-i\' and \'-t\' options')

    experiment(options.questions,
               options.es_server, options.es_index, options.es_type,
               options.query_field, int(options.top_k))
