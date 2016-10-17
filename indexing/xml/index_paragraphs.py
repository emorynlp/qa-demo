#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from optparse import OptionParser
import json
import fnmatch
from elasticsearch import Elasticsearch
from collections import Counter

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')

from es.query import QueryPreprocessor

mapping = '''
{
  "mappings": {
    "paragraph": {
      "properties": {
          "article": {
            "type": "string",
            "index": "not_analyzed"
          },
          "section": {
            "type": "string",
            "index": "not_analyzed"
          },
          "paragraph_id": {
            "type": "string",
            "index": "not_analyzed"
          },
          "text": {
            "type": "string"
          },
          "lemma_text": {
            "type": "string"
          },
          "token_text": {
            "type": "string"
          }
      }
    }
  }
}
'''


def index_paragraphs(directory, json_suffix, es_host, es_index, es_type, b_build_index, force_remove):
    es = Elasticsearch(hosts=[es_host])

    if b_build_index:
        build_index(es, es_index, force_remove)

    query_preprocessor = QueryPreprocessor()

    matched_files = []
    for root, dir_names, file_names in os.walk(directory):
        for filename in fnmatch.filter(file_names, json_suffix):
            matched_files.append(os.path.join(root, filename))

    all_files = len(matched_files)
    iteration = 0
    all_articles = 0
    articles_indexed = 0
    sections_indexed = 0
    paragraphs_indexed = 0

    for f in matched_files:
        articles = json.load(open(f))
        for article in articles:
            all_articles += 1

            # Counter to track duplicated section names (for instance if an article contains two 'History'
            # sections, the second one will have 'History_2' etc.
            sections_id = Counter()
            articles_indexed += 1

            for section in article['sections']:
                sections_id[section['section']] += 1
                sections_indexed += 1

                par_id = 1

                # Set this additional anti-duplicated suffix if necessary (only for duplicates)
                if section['section'] in sections_id and sections_id[section['section']] > 1:
                    section_suffix = sections_id[section['section']]
                else:
                    section_suffix = ''

                for text, token_text, lemma_text in zip(section['paragraphs'], section['paragraphs_tokenized'],
                                                        section['paragraphs_lemmatized']):
                    paragraphs_indexed += 1
                    body = {'text': query_preprocessor.fix_spacing(text),
                            'token_text': query_preprocessor.fix_spacing(token_text),
                            'lemma_text': query_preprocessor.fix_spacing(lemma_text),
                            'article': article['article'],
                            'section': section['section'] + str(section_suffix),
                            'paragraph_id': article['article'].replace(' ', '_') + '-' +
                                            section['section'].replace(' ', '_') + '-' + str(par_id+1)}

                    es.index(index=es_index, doc_type=es_type,
                             body=body,
                             request_timeout=450)

                    par_id += 1

        iteration += 1
        sys.stdout.write("\rFiles parsed: %d/%s" % (iteration, all_files))
        sys.stdout.flush()
    sys.stdout.write("\rFiles parsed: %d/%d" % (iteration, all_files))
    sys.stdout.write('\n')
    sys.stdout.flush()

    print ("All articles: %d\nArticles indexed: %d\nSections indexed: %d\nParagraphs indexed: %d" %
           (all_articles, articles_indexed, sections_indexed, paragraphs_indexed))


def build_index(es, es_index, force_remove):
    if force_remove:
        es.indices.delete(index=es_index, ignore=[400, 404])

    es.indices.create(index=es_index, body=mapping)

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-d', '--directory',
                      action='store',
                      dest='directory',
                      default=None,
                      help="Directory with json files")
    parser.add_option('-s', '--suffix',
                      action='store',
                      dest='file_suffix',
                      default=None,
                      help="Suffix for json files that will be considered in `directory' (Unix wildcard)")
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
    parser.add_option('-b', '--buildindex',
                      action='store_true',
                      dest='build_index',
                      default=False,
                      help="Whether to build the index first")
    parser.add_option("-f", action="store_true", dest="force_remove", default=False, help='If used, the index will'
                                                                                          'be deleted even if exists')
    (options, args) = parser.parse_args()

    if not options.directory or not options.es_server or not options.es_index or not options.file_suffix \
            or not options.es_type:
        raise ValueError('Pass \'-d\', \'s\', \'-e\', \'-i\' and \'-t\' options')

    index_paragraphs(options.directory, options.file_suffix, options.es_server, options.es_index, options.es_type,
                     options.build_index, options.force_remove)
