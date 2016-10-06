# QA Demo: A QA web-based framework for Question Answering over Wikipedia Data

### Installation

1. Prepare your working directory and download pretrained models

```
bash prepare.sh
```

this will create `config.json` file that contains the configuration for the framework.

```
{
  "backend_host": "127.0.0.1", 
  "backend_port": "9500",

  "frontend_key": "<ENTER_YOUR_KEY>",

  "elasticsearch_host": "127.0.0.1",
  "elasticsearch_port": "9200",
  "elasticsearch_index": "wikipedia_08",
  "elasticsearch_type": "paragraph",

  "word2vec_bin_file": "<PATH_TO_GOOGLE_BIN_FILE"
}
```

Two most important elements to modify are `frontend_key` and `word2vec_bin_file`. The former is a unique application key, the latter is the path where Google Word2Vec bin file is located (most likely `GoogleNews-vectors-negative300.bin"`).


2. Install all requirements using `pip`

```
pip install -r requirements.txt
```

3. Install `tensorflow 0.10.0` 
[https://www.tensorflow.org/versions/r0.10/get_started/os_setup.html]
(https://www.tensorflow.org/versions/r0.10/get_started/os_setup.html)

### Run with pretrained models

The framework is ready to run using pretrained models on **Answer Triggering Task**. Simply run a backend and frontend:

```
nohup python ~/projects/qa-demo-mapped/run_backend.py &
```

and

```
gunicorn gunicorn frontend.qa:app
```

the above will run on 127.0.0.1:8000. Run it with a parameter to specify a host and port

```
gunicorn frontend.qa:app -b 127.0.0.1:5000
```

### Contact

If you have any problems or concerns, please contact me: *tomasz.jurczyk@emory.edu*