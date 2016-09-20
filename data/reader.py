class TSVReader:
    """
    This class reads a TSV file with the form of:

    '[question_text]\t[sentence_text]\t[label]'

    Where the label is either 0 or 1.

    It returns a list of question dictionaries
    """
    def parse_file(self, filename):
        samples = []

        with open(filename) as f:
            question_text = None
            question = None
            parsed_questions = 0
            answers_count = 0

            for line in f:
                split_line = line.rstrip().split('\t')

                samples.append((split_line[0], split_line[1], split_line[2]))

        qs = []
        q_entity = dict()
        q_entity['question'] = samples[0][0]
        q_entity['sentences'] = [samples[0][1], ]
        q_entity['labels'] = [int(samples[0][2]), ]

        for s in samples[1:]:
            if s[0] != q_entity['question']:
                # Different question
                qs.append(q_entity)
                q_entity = dict()
                q_entity['question'] = s[0]
                q_entity['sentences'] = [s[1], ]
                q_entity['labels'] = [int(s[2]), ]
                continue

            q_entity['sentences'].append(s[1])
            q_entity['labels'].append(int(s[2]))

        qs.append(q_entity)
        return qs