import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from xml.etree import ElementTree as ET
from pprint import pprint
import codecs
import pickle


class XMLReader:
    def __init__(self):
        self.line_types = {'ARTICLE_START', 'ARTICLE_END', 'SECTION_START', 'OTHER'}

    def extract(self, file_name):
        with io.open(file_name, encoding='utf-8') as f:
            articles = []
            current_article = {}
            current_section = {}
            lines = f.readlines()
            for line in lines:
                line_type, arg_dict = self._extract_line_type(line)

                if line_type == 'ARTICLE_START':
                    current_article['article'] = arg_dict['title'].decode('utf-8')
                    current_article['sections'] = []
                    current_article['id'] = arg_dict['id'].decode('utf-8')
                    current_article['url'] = arg_dict['url'].decode('utf-8')
                    current_section = {'name': u'Abstract', 'paragraphs': []}

                if line_type == 'OTHER':
                    if line.strip() != '':
                        current_section['paragraphs'].append(line.strip())

                if line_type == 'ARTICLE_END':
                    articles.append(current_article)
                    current_article = {}

                if line_type == 'SECTION_START':
                    current_article['sections'].append(current_section)
                    current_section = {'name': arg_dict.decode('utf-8'), 'paragraphs': []}

            return articles

    def _extract_line_type(self, line):
        if line.startswith('<doc id="'):
            return 'ARTICLE_START', ET.fromstring(line.encode('utf-8') + '</doc>').attrib
        elif line.startswith('</doc>'):
            return 'ARTICLE_END', None
        elif line.startswith('<section_name>'):
            return 'SECTION_START', line.strip().lstrip('<section_name>').rstrip('</section_name>').rstrip('.')
        else:
            return "OTHER", None

if __name__ == '__main__':
    x = XMLReader()
    a = x.extract('text/AB/wiki_01')
    pickle.dump(a, open('t.pickle', 'wb'))