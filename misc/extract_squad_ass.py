"""
This scripts prepares a tsv format for SQuAD json files.
Expected input: A list of:

{
  "question": _question_txt_,
  "answerSentenceIds": [_sentence_ids_],
  "sentences": [_sentences_]
}

Output:

question_1\tsentence_1\tlabel
question_1\tsentence_2\tlabel
...
question_2\tsentence_1\tlabel
...
"""
from optparse import OptionParser
import json
import codecs


def parse_file(input_file, output_file):
    json_data = json.load(open(input_file))
    output = codecs.open(output_file, 'w', 'utf-8')

    for q_sample in json_data:
        question_text = q_sample['question']
        answer_ids = [int(i) for i in q_sample['answerSentenceIds']]
        for idx, s in enumerate(q_sample['sentences']):
            output.write(question_text + '\t' + s + '\t')
            if idx in answer_ids:
                output.write('1\n')
            else:
                output.write('0\n')
    output.close()

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option('--input',
                      action='store',
                      dest='input_file',
                      default=None,
                      help="input_file (json)")
    parser.add_option('--output',
                      action='store',
                      dest='output_file',
                      default=None,
                      help="output file (tab separated)")
    (options, args) = parser.parse_args()

    if not options.input_file or not options.output_file:
        raise ValueError('Pass input and output')

    parse_file(options.input_file, options.output_file)
