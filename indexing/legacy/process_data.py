from reader import WikiReader
from pprint import pprint
import json
import sys

"""
This script is to pre-process the wikipedia file from Tim.
Data is slightly pre-process - 'cleaned_text' is created,
which doesn't have any HTML marks. Also, 'section_id' is created.

It has three options:

1. list
List will create a list of all sections. Each element has: original_text
cleaned_text, article, section and section_id

2. dict
Dict option will create a dictionary, where the key is a 'section_id',
and the value is the dictionary with the elements similar to option 'list'.

3. list-article
This option will create a list of articles. All sections of the same article
are merged into one big text field: 'text', and are stored.

"""

if len(sys.argv) != 4:
    raise ValueError("Run with three arguments: [type] [json_source_file] and [output_file]")

type_passed = sys.argv[1]
wiki_filename = sys.argv[2]
output_filename = sys.argv[3]

wiki_reader = WikiReader()

if type_passed == "list":
    p_list = wiki_reader.get_list(wiki_filename)
    print ("Got section list with the len of %d" % len(p_list))
elif type_passed == "dict":
    p_list = wiki_reader.get_dict(wiki_filename)
elif type_passed == "list-article":
    p_list = wiki_reader.get_list_article(wiki_filename)
    print ("Got article list with the len of %d" % len(p_list))
else:
    raise ValueError("Unsupported type, use [list|dict|list-article]")


# p_list = wiki_reader.get_dict(wiki_filename)
# pprint(p_list.keys())
# print ("len of dict is %d" % (len(p_list.keys())))
# pprint (p_list)
json.dump(p_list, open(output_filename, "w"), indent=2)