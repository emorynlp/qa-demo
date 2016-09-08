import os
import sys
import json
from elasticsearch import Elasticsearch
sys.path.append(os.path.dirname(os.path.abspath(__file__+"/../")))
from es.query import QueryPreprocessor

es_hosts = []
es_index = "wikipedia"
es_type = "section"


if len(sys.argv) != 2:
    raise ValueError("Run with a single parameter: [json_file]")

if len(es_hosts) == 0:
    raise ValueError("Fill es_hosts")

es = Elasticsearch(hosts=es_hosts)
query_preprocessor = QueryPreprocessor()

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)

for section in data:
    es.index(index=es_index, doc_type=es_type, body={"section_id": section["section_id"],
                                                     "text": query_preprocessor.fix_spacing(section["cleaned_text"]),
                                                     "original_text": section["original_text"],
                                                     "article": section["article"],
                                                     "section": section["section"]},
             request_timeout=450)