import sys
import json
from pprint import pprint
from es import Elasticsearch

es_server = ["170.140.151.42"]
es_index = "wikipedia-500"
es_type = "paragraph"

if len(sys.argv) != 2:
    raise ValueError("Use with a single argument: [json_with_paragraphs]")

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)


print ("first 5 items:")
it = 0
for elem in data:
    # print ("k: %s")
    pprint(elem)
    it += 1
    if it == 5:
        break


es = Elasticsearch(hosts=es_server)

# for k, v in data.iteritems():
#     print ("v[cleaned_text]: %s" % v["cleaned_text"])
#     es.index(index='wikipedia', doc_type='comment', body={"paragraph_id": v["paragraph_id"],
#                                                           "cleaned_text": v["cleaned_text"]})