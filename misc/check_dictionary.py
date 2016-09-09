import os
import json
import inspect

sc_path = os.path.dirname(os.path.abspath(__file__))

# Load original (our) question list
questions = json.load(open(sc_path + "/../data/original-500/questions.json"))

# Load whole-dictionary
wiki_whole = json.load(open(sc_path + "/../wiki-whole-dict.json"))


not_present = 0
missing_q = []
for i in questions:
    if i["paragraph_id"] not in wiki_whole:
        missing_q.append(i)
        not_present += 1

print ("Out of %d questions, %d of their paragraphs are not present in wiki dump" % (len(questions), not_present))
