"""
This script extracts SQuAD files to the format of:

[
 {'question': <question_text>,
  'article': <article_question_from>,
  'section': <section_question_from>,
 },
 ...
]
"""

import sys
from optparse import OptionParser
import json
import pickle

reload(sys)
sys.path.insert(0, '../')
sys.setdefaultencoding('utf-8')


def process(input_file, output_file):
    loaded_json = json.load(open(input_file))
    data = loaded_json['data']
    q_list = []

    for d in data:
        for paragraph in d['paragraphs']:
            if paragraph['wiki_paragraph']:
                article = paragraph['wiki_paragraph']['article_title']
                section = paragraph['wiki_paragraph']['section_title']

                if section == "ABSTRACT":
                    section = 'Abstract'

                paragraph_number = paragraph['wiki_paragraph']['paragraph_id']

                for q in paragraph['qas']:
                    q_dict = dict()
                    q_dict['article'] = article
                    q_dict['section'] = section
                    q_dict['paragraph_number'] = paragraph_number
                    q_dict['question'] = q['question']
                    q_dict['id'] = q['id']
                    q_dict['answer'] = q['answers'][0]['text']

                    q_list.append(q_dict)

    print 'Retrieved %d questions' % len(q_list)
    pickle.dump(q_list, open(output_file, 'w'))


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('-i', '--input',
                      action='store',
                      dest='input_file',
                      default=None,
                      help="Input file")
    parser.add_option('-o', '--output',
                      action='store',
                      dest='output_file',
                      default=None,
                      help="Output file")
    (options, args) = parser.parse_args()

    if not options.input_file or not options.output_file:
        raise ValueError('Pass \'-i\' and \'-o\' options')

    process(options.input_file, options.output_file)
