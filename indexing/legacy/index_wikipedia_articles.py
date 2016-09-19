import os
import sys
import json
from elasticsearch import Elasticsearch
sys.path.append(os.path.dirname(os.path.abspath(__file__+"/../")))
from es.query import QueryPreprocessor

es_hosts = []
es_index = "wikipedia"
es_type = "article"


if len(sys.argv) != 2:
    raise ValueError("Run with a single parameter: [json_file]")

if len(es_hosts) == 0:
    raise ValueError("Fill es_hosts")

es = Elasticsearch(hosts=es_hosts)
query_preprocessor = QueryPreprocessor()

mapping = '''
{
  "mappings": {
    "article": {
      "properties": {
          "article": {
            "type": "string",
            "index": "not_analyzed"
          },
          "text": {
            "type": "string"
          }
      }
    },
    "section": {
      "properties": {
          "article": {
            "type": "string",
            "index": "not_analyzed"
          },
          "section": {
            "type": "string",
            "index": "not_analyzed"
          },
          "section_id": {
            "type": "string",
            "index": "not_analyzed"
          },
          "text": {
            "type": "string"
          },
          "original_text": {
            "type": "string"
          }
      }
    }
  }
}
'''

es.indices.delete(index=es_index, ignore=[400, 404])
es.indices.create(index=es_index, body=mapping)

with open(sys.argv[1]) as data_file:
    data = json.load(data_file)

for article in data:
    es.index(index=es_index, doc_type=es_type, body={"text": query_preprocessor.fix_spacing(article["text"]),
                                                     "article": article["article"]},
             request_timeout=450)