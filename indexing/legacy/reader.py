import json
import nltk
import re

class WikiReader(object):
    """
    Reader for Wikipedia json file
    """

    SKIPPED_SECTIONS = {'See also', 'See Also', 'References', 'Bibliography', 'Further reading',
                        'External links', 'Footnotes', 'References and sources', 'Sources', 'Visual summary',
                        'Notes', 'Textbooks', 'Printed sources', 'Physiology', 'Equestrianism', 'Biomolecule',
                        }

    LI_MARKS = {'</li><li>', '<li>', '</li>'}

    def __init__(self):
        pass

    def get_list(self, w_filename):
        li = []

        with open(w_filename) as data_file:
            data = json.load(data_file)

        for json_item in data:
            try:
                obj = self.extract_entity(json_item)

                if obj:
                    li.append(obj)
            except ValueError:
                raise ValueError("json can't be parsed")

        return li

    def get_dict(self, w_filename):
        di = dict()

        with open(w_filename) as data_file:
            data = json.load(data_file)

        for json_item in data:
            try:
                obj = self.extract_entity(json_item)

                if obj:
                    if obj["section_id"] in di:
                        # raise KeyError("duplicated key in dictionary (paragraph_id): %s" % obj["paragraph_id"])
                        print ("duplicated key in dictionary, skipping this one. paragraph_id: %s" % obj["section_id"])

                    else:
                        di[obj["section_id"]] = obj

            except ValueError:
                raise ValueError("json can't be parsed")

        return di

    def get_list_article(self, w_filename):
        li = []

        with open(w_filename) as data_file:
            data = json.load(data_file)

        article = data[0]["Name"]
        di = {"text": "", "article": article}

        for json_item in data:
            try:
                obj = self.extract_entity(json_item)

                if obj:
                    if obj["article"] != article:
                        # print ("About to store article: %s" % (article))
                        # This is a new article
                        li.append(di)
                        article = obj["article"]
                        di = {"text": obj["section"], "article": article}
                    else:
                        # Same one, collect
                        di["text"] = di["text"] + " " + obj["cleaned_text"]


            except ValueError:
                raise ValueError("json can't be parsed")

        # The last one is to store
        # print ("About to store article: %s" % (article))
        li.append(di)

        return li

    def extract_entity(self, entity):
        if entity["Section"] in self.SKIPPED_SECTIONS:
            return {}

        parsed_item = dict()
        parsed_item["article"] = entity["Name"]
        parsed_item["section"] = entity["Section"]

        checked_text = re.sub(r'^('+re.escape(parsed_item["article"])+'|'+re.escape(parsed_item["section"])+'\.?)',
                              '',
                              entity["Text"])
        #checked_text = re.sub(r'^('+parsed_item["name"]+')', '', entity["Text"])
        #checked_text = re.sub(r'^('+parsed_item["section"]+' \(\+\)\.)', '', entity["Text"])
        #checked_text = re.sub(r'^(Addition \(\+\)\.?)', '', entity["Text"])
        #re.escape(a)
        #checked_text = re.sub(r'^('+re.escape(parsed_item["section"])+'\.?)', '', entity["Text"])

        parsed_item["original_text"] = checked_text
        parsed_item["cleaned_text"] = re.sub(r'(<li>|</li><li>|</li>|<\\/li><li>)', ' ', checked_text)

        # The id for each paragraph is [name]-[section] (spaces to underscores if appear)
        parsed_item["section_id"] = re.sub(r' ', '_', parsed_item["article"]) + "-" + \
                                    re.sub(r' ', '_', parsed_item["section"])

        return parsed_item